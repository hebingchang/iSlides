import sys
sys.path.insert(0, "../lib")
import Leap
import sendkeys

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    flag = {"direction": -1, "count": 0, "volume": 0, "swipe_starttime": 0, "swipe_lastendtime": 0, "last_direction": -1}
    min_during_time = 1331100
    volume_lastendtime_flag = volume_starttime_flag = 0
    volume_last_diretion = -1

    swipe_min_frames = 2
    swipe_volume_min_frames = 4
    swipe_min_delta_y = 0.3

    def on_init(self, controller):
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
        controller.config.set("Gesture.Swipe.MinLength", 100.0)
        controller.config.set("Gesture.Swipe.MinVelocity", 160.0)

        controller.config.set("Gesture.KeyTap.MinDownVelocity", 1.0)
        controller.config.set("Gesture.KeyTap.HistorySeconds", 1.0)
        controller.config.set("Gesture.KeyTap.MinDistance", 0.1)

        controller.set_policy(Leap.Controller.POLICY_BACKGROUND_FRAMES)
        controller.config.save()

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
        for gesture in gestures:
            if gesture.type is Leap.Gesture.TYPE_SWIPE:
                swipe = Leap.SwipeGesture(gesture)
                swipe_direction = swipe.direction
                swipe_pointable = swipe.pointable
                swipe_speed = swipe.speed
                print swipe_direction, swipe_speed
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
                    self.flag["volume"] += 1
                    if self.volume_starttime_flag == 0: self.volume_starttime_flag = frame.timestamp
                    print self.volume_last_diretion
                    if self.flag["volume"] > self.swipe_volume_min_frames and (self.volume_starttime_flag - self.volume_lastendtime_flag > self.min_during_time or self.volume_last_diretion == 1):
                        sendkeys.arrow_input("volume_up")
                        self.flag["volume"] = 0
                        self.volume_last_diretion = 1
                elif swipe_direction.y < 0 and abs(swipe_direction.x) < self.swipe_min_delta_y:
                    self.flag["direction"] = 3 # down
                    self.flag["volume"] += 1
                    if self.volume_starttime_flag == 0: self.volume_starttime_flag = frame.timestamp
                    print self.volume_last_diretion
                    if self.flag["volume"] > self.swipe_volume_min_frames and (self.volume_starttime_flag - self.volume_lastendtime_flag > self.min_during_time or self.volume_last_diretion == 0):
                        sendkeys.arrow_input("volume_Down")
                        self.flag["volume"] = 0
                        self.volume_last_diretion = 0

        if len(gestures) == 0:
            if self.flag["direction"] == 1 and (self.flag["swipe_starttime"] - self.flag["swipe_lastendtime"] > self.min_during_time or self.flag["last_direction"] == 1):
                sendkeys.arrow_input("right_arrow")
                self.flag["swipe_lastendtime"] = frame.timestamp
                self.flag["last_direction"] = 1
            elif self.flag["direction"] == 0 and (self.flag["swipe_starttime"] - self.flag["swipe_lastendtime"] > self.min_during_time or self.flag["last_direction"] == 0):
                sendkeys.arrow_input("left_arrow")
                self.flag["swipe_lastendtime"] = frame.timestamp
                self.flag["last_direction"] = 0

            self.flag["count"] = 0
            self.flag["direction"] = -1
            self.flag["swipe_starttime"] = 0
            if self.volume_starttime_flag != 0:
                self.volume_lastendtime_flag = frame.timestamp
                self.volume_starttime_flag = 0




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
