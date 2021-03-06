from enum import Enum
import behavior
import _GoToPoint_
import rospy
from utils.functions import *
from utils.config import *

class GoToBall(behavior.Behavior):
    """docstring for GoToBall"""
    class State(Enum):
        setup = 1 
        course_approach = 2
        fine_approach = 3

    def __init__(self,course_approch_thresh =  DISTANCE_THRESH/3,continuous=False):

        super(GoToBall,self).__init__()

        self.name = "GoToBall"

    	self.power = 7.0

        self.target_point = None
        

        self.course_approch_thresh = course_approch_thresh

        self.ball_dist_thresh = BOT_BALL_THRESH

        self.behavior_failed = False


        self.add_state(GoToBall.State.setup,
            behavior.Behavior.State.running)

        self.add_state(GoToBall.State.course_approach,
            behavior.Behavior.State.running)
        
        self.add_state(GoToBall.State.fine_approach,
            behavior.Behavior.State.running)

        self.add_transition(behavior.Behavior.State.start,
            GoToBall.State.setup,lambda: True,'immediately')

        self.add_transition(GoToBall.State.setup,
            GoToBall.State.fine_approach,lambda: self.fine_approach(),'ball_in_vicinity')

        self.add_transition(GoToBall.State.setup,
            GoToBall.State.course_approach,lambda: self.course_approach(),'setup')

        self.add_transition(GoToBall.State.course_approach,
            GoToBall.State.fine_approach,lambda:self.at_target_point(),'complete')

        self.add_transition(GoToBall.State.fine_approach,
            behavior.Behavior.State.completed,lambda:self.at_ball_pos(),'complete')

        self.add_transition(GoToBall.State.setup,
            behavior.Behavior.State.failed,lambda: self.behavior_failed,'failed')

        self.add_transition(GoToBall.State.course_approach,
            behavior.Behavior.State.failed,lambda: self.behavior_failed,'failed')

        self.add_transition(GoToBall.State.fine_approach,
            behavior.Behavior.State.failed,lambda: self.behavior_failed,'failed')
    
    def add_kub(self,kub):
        self.kub = kub

    def add_theta(self,theta):
        self.theta = theta

    def fine_approach(self):
        return self.ball_in_vicinity() 

    def course_approach(self):
        return not self.ball_in_vicinity() 
    # def target_present(self):
    #     return not ball_in_front_of_bot(self.kub) and self.target_point is not None 

    def at_target_point(self):
        return vicinity_points(self.target_point,self.kub.get_pos(),thresh= self.course_approch_thresh)


    def ball_in_vicinity(self):
        if ball_in_front_of_bot(self.kub):
            return True
        return False

    def at_ball_pos(self):
        error = 10
        return vicinity_points(self.kub.get_pos(),self.kub.state.ballPos,thresh=self.ball_dist_thresh+error) 

    def terminate(self):
        super().terminate()
        
    def on_enter_setup(self):
        pass
    def execute_setup(self):
        pass
        
    def on_exit_setup(self):
        pass

    def on_enter_course_approach(self):
        self.target_point = getPointBehindTheBall(self.kub.state.ballPos,self.theta)
        self.target_point = self.kub.state.ballPos
        _GoToPoint_.init(self.kub, self.target_point, self.theta)
        pass

    def execute_course_approach(self):
        start_time = rospy.Time.now()
        start_time = 1.0*start_time.secs + 1.0*start_time.nsecs/pow(10,9)   
        generatingfunction = _GoToPoint_.execute(start_time,self.course_approch_thresh,True)
        for gf in generatingfunction:
            self.kub,target_point = gf
            # self.target_point = getPointBehindTheBall(self.kub.state.ballPos,self.theta)
            self.target_point = self.kub.state.ballPos
            if not vicinity_points(self.target_point,target_point,thresh=BOT_RADIUS*3.5):
                self.behavior_failed = True
                break


    def on_exit_course_approach(self):
        pass

    def on_enter_fine_approach(self):
        theta = self.kub.get_pos().theta
        _GoToPoint_.init(self.kub, self.kub.state.ballPos, theta)
        pass

    def execute_fine_approach(self):
        start_time = rospy.Time.now()
        start_time = 1.0*start_time.secs + 1.0*start_time.nsecs/pow(10,9)   
        generatingfunction = _GoToPoint_.execute(start_time,self.ball_dist_thresh)
        for gf in generatingfunction:
            self.kub,ballPos = gf
            
            if not vicinity_points(ballPos,self.kub.state.ballPos,thresh=BOT_RADIUS):
                self.behavior_failed = True
                break




    def disable_kick(self):
        self.power = 0.0

    def on_exit_fine_approach(self):
        #self.disable_kick()
        self.kub.kick(self.power)
        self.kub.execute()
        pass





