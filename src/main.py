import sys

sys.path.insert(0, "../lib")
import Leap
import sendkeys
import win32api

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    flag = {"direction": -1, "count": 0, "swipe_starttime": 0, "swipe_lastendtime": 0, "last_direction": -1}
    volume_flag = {"volume": 0, "volume_lastendtime": 0, "volume_starttime": 0, "last_diretion": -1}
    min_during_time = 1330000
    min_same_direction_time = 200000
    swipe_min_frames = 2
    swipe_volume_min_frames = 4
    swipe_min_delta_y = 0.3
    mouse_speed_x_multiply = 85.4
    mouse_speed_y_multiply = 40.4

    is_mouse_controlled = False
    mousebegin = True
    width = 0
    height = 0
    xpos = 0
    ypos = 0

    is_pen_valid = -1

    def on_init(self, controller):
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
        #controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
        controller.config.set("Gesture.Swipe.MinLength", 100.0)
        controller.config.set("Gesture.Swipe.MinVelocity", 160.0)

        #controller.config.set("Gesture.KeyTap.MinDownVelocity", 1.0)
        #controller.config.set("Gesture.KeyTap.HistorySeconds", 1.0)
        #controller.config.set("Gesture.KeyTap.MinDistance", 0.1)

        controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
        controller.config.save()

        self.width = win32api.GetMonitorInfo(win32api.EnumDisplayMonitors(None, None)[0][0])["Monitor"][2]
        self.height = win32api.GetMonitorInfo(win32api.EnumDisplayMonitors(None, None)[0][0])["Monitor"][3]
        self.xpos = int(self.width / 2)
        self.ypos = int(self.height / 2)


        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % (
              #frame.id, frame.timestamp, len(frame.hands), len(frame.fingers))

        gestures = frame.gestures()
        righthand = frame.hands.rightmost
        pinky_position = righthand.fingers[4].bone(Leap.Bone.TYPE_DISTAL).center
        ring_position = righthand.fingers[3].bone(Leap.Bone.TYPE_DISTAL).center
        finger_position = righthand.fingers[1].bone(Leap.Bone.TYPE_DISTAL).center
        hand_position = righthand.palm_position

        is_fisting = (0.0 < point_distance(ring_position, hand_position) < 45.0 and 0.0 < point_distance(pinky_position,
                                                                                              hand_position) < 45.0)

        if is_fisting and not frame.hands.is_empty:
            self.is_mouse_controlled = True
        else:
            if frame.hands.is_empty and self.is_pen_valid and self.is_mouse_controlled:
                sendkeys.multi_input("left_control", "p")
                sendkeys.mouse_up()
                self.is_pen_valid = False
                pen_switch = False
            self.is_mouse_controlled = False
            self.mousebegin = True
            (self.xpos, self.ypos) = win32api.GetCursorPos()
            #self.xpos = self.width / 2
            #self.ypos = self.height / 2

        pen_valid_temp = point_distance(finger_position, hand_position) > 80 and self.is_mouse_controlled
        if self.is_pen_valid and not pen_valid_temp:
            sendkeys.mouse_up()
            sendkeys.multi_input("left_control", "p")
        elif not self.is_pen_valid and pen_valid_temp:
            sendkeys.multi_input("left_control", "p")
            sendkeys.mouse_down()
        self.is_pen_valid = pen_valid_temp


        if self.is_mouse_controlled:
            if self.is_pen_valid:
                hand = frame.hands.rightmost
                hand_speed = hand.palm_velocity
                self.xpos = self.xpos + int(hand_speed.x / 40)
                self.ypos = self.ypos - int(hand_speed.y / 40)
                if self.xpos < 0:
                    self.xpos = 0
                if self.xpos > self.width:
                    self.xpos = self.width
                if self.ypos < 0:
                    self.ypos = 0
                if self.ypos > self.height:
                    self.ypos = self.height
                sendkeys.mouse_move_down(self.xpos, self.ypos)

            else:
                if self.mousebegin:
                    self.mousebegin = False
                    sendkeys.mouse_move(self.xpos, self.ypos)
                else:
                    hand = frame.hands.rightmost
                    hand_speed = hand.palm_velocity
                    self.xpos = self.xpos + int(hand_speed.x / self.width * self.mouse_speed_x_multiply)
                    self.ypos = self.ypos - int(hand_speed.y / self.height * self.mouse_speed_y_multiply)
                    if self.xpos < 0:
                        self.xpos = 0
                    if self.xpos > self.width:
                        self.xpos = self.width
                    if self.ypos < 0:
                        self.ypos = 0
                    if self.ypos > self.height:
                        self.ypos = self.height
                    sendkeys.mouse_move(self.xpos, self.ypos)

        for gesture in gestures:
            #righthand = frame.hands.rightmost
            #circle = Leap.CircleGesture(gesture)
            #print circle.pointable.direction.angle_to(circle.normal),
            #print point_distance(ring_position, hand_position),
            #print point_distance(pinky_position, hand_position),
            #print circle.pointable.direction.angle_to(circle.normal)

            if not self.is_mouse_controlled:
                if gesture.type is Leap.Gesture.TYPE_SWIPE:
                    swipe = Leap.SwipeGesture(gesture)
                    swipe_direction = swipe.direction
                    swipe_pointable = swipe.pointable
                    swipe_speed = swipe.speed
                    if swipe_direction.x > 0 and abs(swipe_direction.y) < self.swipe_min_delta_y:
                        self.flag["direction"] = 0
                        self.flag["count"] += 1
                        if self.flag["swipe_starttime"] == 0: self.flag["swipe_starttime"] = frame.timestamp
                    elif swipe_direction.x < 0 and abs(swipe_direction.y) < self.swipe_min_delta_y:
                        self.flag["direction"] = 1
                        self.flag["count"] += 1
                        if self.flag["swipe_starttime"] == 0: self.flag["swipe_starttime"] = frame.timestamp
                    elif swipe_direction.y > 0 and abs(swipe_direction.x) < self.swipe_min_delta_y:
                        self.flag["direction"] = 2 # up
                        self.volume_flag["volume"] += 1
                        if self.volume_flag["volume_starttime"] == 0: self.volume_flag["volume_starttime"] = frame.timestamp
                        if self.volume_flag["volume"] > self.swipe_volume_min_frames and (self.volume_flag["volume_starttime"] - self.volume_flag["volume_lastendtime"] > self.min_during_time or self.volume_flag["last_diretion"] == 1):
                            sendkeys.arrow_input("volume_up")
                            self.volume_flag["volume"] = 0
                            self.volume_flag["last_diretion"] = 1
                    elif swipe_direction.y < 0 and abs(swipe_direction.x) < self.swipe_min_delta_y:
                        self.flag["direction"] = 3 # down
                        self.volume_flag["volume"] += 1
                        if self.volume_flag["volume_starttime"] == 0: self.volume_flag["volume_starttime"] = frame.timestamp
                        if self.volume_flag["volume"] > self.swipe_volume_min_frames and (self.volume_flag["volume_starttime"] - self.volume_flag["volume_lastendtime"] > self.min_during_time or self.volume_flag["last_diretion"] == 0):
                            sendkeys.arrow_input("volume_Down")
                            self.volume_flag["volume"] = 0
                            self.volume_flag["last_diretion"] = 0



        if len(gestures) == 0:
            if self.flag["direction"] == 1 and (self.flag["swipe_starttime"] - self.flag["swipe_lastendtime"] > self.min_during_time or (self.flag["last_direction"] == 1 and self.flag["swipe_starttime"] - self.flag["swipe_lastendtime"] > self.min_same_direction_time)):
                sendkeys.arrow_input("right_arrow")
                self.flag["swipe_lastendtime"] = frame.timestamp
                self.flag["last_direction"] = 1
            elif self.flag["direction"] == 0 and (self.flag["swipe_starttime"] - self.flag["swipe_lastendtime"] > self.min_during_time or (self.flag["last_direction"] == 0 and self.flag["swipe_starttime"] - self.flag["swipe_lastendtime"] > self.min_same_direction_time)):
                sendkeys.arrow_input("left_arrow")
                self.flag["swipe_lastendtime"] = frame.timestamp
                self.flag["last_direction"] = 0

            self.flag["count"] = 0
            self.flag["direction"] = -1
            self.flag["swipe_starttime"] = 0
            if self.volume_flag["volume_starttime"] != 0:
                self.volume_flag["volume_lastendtime"] = frame.timestamp
                self.volume_flag["volume_starttime"] = 0




            # Get hands
        '''for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"

            print "  %s, id %d, position: %s" % (
                handType, hand.id, hand.palm_position)

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            # Calculate the hand's pitch, roll, and yaw angles
            print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
                direction.pitch * Leap.RAD_TO_DEG,
                normal.roll * Leap.RAD_TO_DEG,
                direction.yaw * Leap.RAD_TO_DEG)

            # Get arm bone
            arm = hand.arm
            print "  Arm direction: %s, wrist position: %s, elbow position: %s" % (
                arm.direction,
                arm.wrist_position,
                arm.elbow_position)

            # Get fingers
            for finger in hand.fingers:

                print "    %s finger, id: %d, length: %fmm, width: %fmm" % (
                    self.finger_names[finger.type],
                    finger.id,
                    finger.length,
                    finger.width)

                # Get bones
                for b in range(0, 4):
                    bone = finger.bone(b)
                    print "      Bone: %s, start: %s, end: %s, direction: %s" % (
                        self.bone_names[bone.type],
                        bone.prev_joint,
                        bone.next_joint,
                        bone.direction)

        if not frame.hands.is_empty:
            print ""
        '''

def point_distance(point1, point2):
    return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2) ** 0.5

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
