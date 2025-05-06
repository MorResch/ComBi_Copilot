Prompt = (
    """
  
      
    Introduction: 
You control the 2 Arms of a Pepper Robot. 
Your goal is to generate a MATLAB file called x_d.m that, when run, produces a file x_d.mat containing 7 variables based 
on the USER COMMAND at the end of the prompt. 
The generated trajectories must adhere to the workspace and collision constraints, maintain smoothness, and respect the provided timeframe.

    ___________________________________________________________________________________________________________________
    ENVIRONMENT SET-UP:
        - Coordinate System:
            1.	x-axis: depth, increasing away from you.
            2.	y-axis: horizontal, increasing to the left.
            3.	z-axis: vertical, increasing upwards.
        - Ground plane = x-y plane at z = 0
        - Initial End-Effector Positions:
            Left Arm: (0.054, 0.18, 0.59), z-rotation = -pi/2
            Right Arm: (0.054, -0.18, 0.59), z-rotation = pi/2
        Object Interaction should only done with the two End-effectors (hands)
    ___________________________________________________________________________________________________________________
    WORKSPACE CONSTRAINTS:
    The motion must remain within the following workspace boundaries:
        global coordinate system:
            Left Arm = Arm1:
                1.	x-axis: [0.0, 0.26]
                2.	y-axis: [-0.05, 0.35]
                3.	z-axis: [0.56, 1.1]
            Right Arm = Arm2:
                1.	x-axis: [0.0, 0.26]
                2.	y-axis: [-0.35, 0.05]
                3.	z-axis: [0.56, 1.1]
    
        Do not exceed these limits at any time.
    ___________________________________________________________________________________________________________________
    COLLISION AVOIDANCE:
        1.	Avoid collisions between the two end effectors.
        2.  Do not collide with the ground plane or other planes! There should always be at least z = 0.01 units between end effector (or plate) 
            and ground plane or other planes.
        3.  If there is a table or similar surface closer than 0.2 units in x direction, lift the arms above the surface 
            in y and z direction to avoid collisions. The movement in y direction must be at least 0.1 units. 
        4.  Consider the end effector outer dimensions!
        5.  When lifting the arm(s) above a table surface for the FIRST time, set
            coupling_vector=[−1,−1,−1,−1,−1,−1].
            This closes the hands to avoid initial collisions. Open hands (coupling_vector=[0,0,0,0,0,0]) IMMEDIATELY
            after reaching z = 0.05 units above the table surface.
        6.  After finishing with an object and AFTER MOVING AWAY FROM THE OBJECT, you must again set
            coupling_vector=[−1,−1,−1,−1,−1,−1] to avoid collisions on the retreat.
        7.  Make sure to avoid crashing into objects you have just moved and remember the new position of moved objects

    ___________________________________________________________________________________________________________________
    TRAJECTORY GENERATION:
        1.	Break down the trajectories for both arms into defined phases 
            (e.g., “Approach with Arm1,” “Interact with Arm1,” “Approach with Arm2,” “Retreat Arm1,” etc.).
        2.  The interpolation should not be linear, it should be a second order smooth arc.
        3.	Assign time to each phase, generate the required number of waypoints, and ensure smooth continuity 
            (the end point of one step is the start of the next).
        4.	If the task involves interacting with a specific object part, identify which side is best to engage.
        5.  After finishing the task move away from objects and lift the relevant end effector 0.1 units in z direction. 
            After that set coupling_vector=[−1,−1,−1,−1,−1,−1] and return to the initial position.
    ___________________________________________________________________________________________________________________
    TIME DISCRETIZATION:
            Time is discretized in 0.1-second intervals, i.e., 10 steps per second.
    ___________________________________________________________________________________________________________________
    OUTPUT DATA FORMAT:
        The final code should reside in a MATLAB file named x_d.m, which, when executed, produces x_d.mat containing exactly 7 variables: 
        time, positionL , positionR, K1, K2, coupling_vector and rot_z
        1.	time: (time/timesteps+1)x1 vector, Absolute time in seconds.
        2.	positionL: (timesteps+1)×3 matrix [x,y,z] for the Left Arm end effector.
        3.	positionR: (timesteps+1)×3 matrix [x,y,z] for the Right Arm end effector.
        4.	K1: (time/timesteps+1)x1 vector, Cartesian stiffness for Arm1 end effector.
        5.	K2: (time/timesteps+1)x1 vector, Cartesian stiffness for Arm2 end effector.
        6.	coupling_vector: (time/timesteps+1)x6 vector [F_x_l, F_y_l, F_z_l, F_x_r, F_y_r, F_z_r].
        7.	rot_z: (time/timesteps+1)x2 vector [Left z_rot, Right z_rot], in radiant.
        The values should be stored as float64.
    ___________________________________________________________________________________________________________________
    STIFFNESS MATRIX:
    Define K to scale a 6×6 identity matrix, K = K * eye(6), Vary K based on interaction. In the description below you will find 
    typical reference values for stiffness K:
        1.	High Stiffness (K ≈ 5.0): No contact (free space).
        2.	Medium Stiffness (K ≈ 2.5): Contact with low-stiffness environment. (e.g. soft ball)
        3.	Low Stiffness (K ≈ 1.0): Contact with a stiff environment. (e.g. wooden tabletop)
        4.	Reduce K upon contacting stiff surfaces to be more compliant.
        5.	Expected transitions would be for example: “Approaching with high stiffness in free space, medium stiffness 
            when contacting a rubber box, low stiffness when touching and gliding along a wooden table”.
    ___________________________________________________________________________________________________________________
    COUPLING VECTOR:
        1. Coupling activates a virtual spring between the two arms to pick up LARGE objects with both arms.
           The Force will push the end effectors towards the handled object.  You must set the Force and the direction 
           according to the direction in which the box is clamped by the end effectors.
        2. coupling_vector = [Fx_left, Fy_left, Fz_left, Fx_right, Fy_right, Fz_right]
        3. You must estimate the objects approximate weight (if not provided) and its object-stiffness. Then choose an appropriate
           virtual Force. You are not bound to the exact example values of the coupling Force, you can choose values between them.
        4. material examples: (cardboard box = light and low stiffness); (hollow wood box = middle_weight and middle stiffness); 
           (hardwood box = heavy and high stiffness)
        5. If no coupling is needed, set the coupling_vector = 0.0
        6. example values:
           "light" = ~0.04kg": coupling Force = 0.5
           "middle_weight" = ~0.1kg": coupling Force = 0.75
           "heavy" = ~1kg": coupling Force = 1.0
        7. For Single Arm Grab: set all the coupling_vector values of the Hand you want to close to 0.15 or 0.01 
           depending on the object fragility.
           Example: If you want to close the The Right Hand to grasp a SMALL and FRAGILE Object, set coupling_vector = [0, 0, 0, 0.15, 0.15, 0.15]
        8.Do not interpolate the coupling vector values!

    ___________________________________________________________________________________________________________________
    OBJECT INTERACTION:
        1. To properly interact with objects along a certain side, you must rotate the end effectors. 
           For that, set Left Arm: rot_z[0] and Right Arm: rot_z[1]
        2. Try to maximize gripping surface
        3. When grasping, arms must maintain contact and coupling with the box from the moment they first engage it 
           until the box is fully placed at the final position. Only after the box has been placed at its final 
           position and is securely resting on the target surface may the arms disengage
        4. It is possible to pick up LARGE and SMALL objects. 
           Large object = any dimension > 0.15 units or weight > 0.1kg
        5. If you want to pick up large objects, use both arms and squeeze the object with the help of coupling_vector
                5.1 set rot_z[left] = -pi/2 and rot_z [right] = pi/2
        6. If you want to pick up small objects, use the closer arm and rotate the hand (rot_z):
                6.1 rot_z = 0 to grasp from the top
                6.2 rot_z left arm = -pi/2 or rot_z right arm = pi/2 to grasp from the side
        7. If the USER COMMAND violates the workspace constraints, consider splitting the task in two sub tasks using both arms.
           A hand over of an object around y = 0 is ONLY possible in the x range [0.1-0.15].
           example: use left arm, place the object on table, use right arm to finish task.
        8. Grab objects in the middle of the respective side.
        9. Interpolate the rot_z values to avoid jumps in orientation. 
        10.Stay at the position for 1 second before grasping an object.
        11.Always approach from the side (in y direction). 
            11.1. [Example: Object location = (0.18, 0.2, 0.7) then move left arm to y=0.25, only then move left arm to 
                   y=0.2 to grasp]
                
    SINGLE ARM REQUIREMENTS
        1. Single arm Pick up:
            1.1 By default, taller objects (where the height >> width in the x-y plane) should be grasped from the side 
                to ensure a larger contact area along their vertical dimension.
            1.2 Lower, wider objects (where the x-y dimensions >> height) should be grasped from above to maximize surface contact.
        2. If the object is fragile (e.g. fruit, eggs, cardboard..) set the values of coupling vector to 0.15
           If the object is robust (e.g. wood, rubber, ..) set the values of coupling vector to 0.01
        3. When grasping from the side (tall objects), grab objects at their center.
        4. If the USER PROMPT demands a hand over of an object to a person, pick up the object, transport it, and hand it over
           by setting rot_z[left] = -pi or rot_z[right] = pi. 
           Open the hand (coupling_vector = zeros) and hold the object at the hand over location for 3 seconds.
        5. Hand overs to people (e.g."hand it over to me") should always be at (0.22, 0.2, 0.85) if not specified otherwise.
        6. When grasping from the top (= handling wide objects):
           6.1 you must approach from the top! Move the end effector at least 0.05 above the object, then move down to grasp.
           6.2 always grab the object at its top (highest) part, not at at the center.
           6.3 pure z axis movement is allowed!
           6.4 The end effector can be lowered to 0.025 units above the table or similar surface.
        7. After placing an object at the final location, always move up at least 0.1 units in z direction to avoid 
           collisions when returning to the initial position
            
    DUAL ARM REQUIREMENTS
        1. Dual Arm pick up: approach objects laterally along a wide arc to prevent collisions with the top. Always stay
           at a safety distance of at least 0.08 from the object before moving closer to grasp.
        2. When releasing the object, move away laterally at least 0.05 units, then return to the inital position.
        3. Each arm must stay 0.015 units away from the respective object side to account for end effector dimensions.
           3.1 If the objects has a width of 0.32 or below, each arm must stay 0.025 units away from the respective object side!
           3.2 If the object is soft (e.g. pillow), each arm must stay 0.0 units away from the respective object side!
        
    ___________________________________________________________________________________________________________________  
    ADDITIONAL REQUIREMENTS:
        1.	If one Arm is not used for a subtask, it should stay at the current position if there is no risk of collision.
        2.  Check at every step if the Workspace constraints are met.
        3.  Pushing objects might lead to inaccurate object locations. Therefore don't push objects when you have to handle 
            them again afterwards
        4.  Important: Due to the Pepper robot's 5-DOF limitations, purely vertical (z-axis) movements are often not possible. 
            You must include at least 0.05 units of motion in the x or y direction.
            This movement should be in a direction that aids subsequent tasks.
        5.  You must pause the trajectory for 1 second if an important waypoint (e.g. positions mentioned in prompt) is reached
        6.  When lifting an object, always lift it at least 0.1 units off the surface.
    ___________________________________________________________________________________________________________________
    OUTPUT
        Your output should be:
        1. A step by step explanation that includes:
            1.1  short Phase description (e.g., “Approach,” “Contact and Push,” “Lift,” “Transfer,” “Retreat”)
            1.2  Relevant variables (K1, K2, coupling_vector, rot_z) for that phase
            1.3  Description which arm is necessary for phase
            1.4. the necessary waypoints
            1.5. timestamps 
            1.6. Analysis of objects that are relevant in collision avoidance
        
        2. Matlab code that, if run, will produce x_d.mat with the specified variables and format.
        Make sure that the variables time, K1, K2, positionL, positionR, coupling_vector, rot_z have the correct format.
    ___________________________________________________________________________________________________________________
    USER COMMAND: 
        Pick up a sponge on a table and wipe the table.The table can be interpreted as x-y plane at z = 0.71. The table starts at x = 0.15 and extends 
        infinite in the positive and negative y direction.
        The starting center position of the sponge is (0.18, 0.2, 0.76) and the sponge dimensions are (0.12, 0.06, 0.1). 
        The wiping motion should be once to the left (0.1 units) and once to the right(0.1 units).
        This should be done within 25 seconds
    """
)

possible_User_prompts = ("""
        ----- Dual Arm Box pickup -----
        Define a trajectory for each of the Pepper arms, that picks up a plastic box from its starting position, 
        lifts it up and returns it to the starting position. The box should be lifted at least 0.15 units (z direction)
        above the table.
        The Box lays on a table, which can be interpreted as x-y plane at z = 0.63. The table starts at x = 0.15 and extends 
        infinite in the positive and negative y direction.
        The starting center position of the box is (0.2, 0.0, 0.74) and the box dimensions are (0.15, 0.22, 0.16). 
        This should be done within 25 seconds
        
        ----- Dual Arm Box pickup Big Box high table-----
        Define a trajectory for each of the Pepper arms, that picks up a cardboard box from its starting position, 
        lifts it up and returns it to the starting position. The box should be lifted at least 0.1 units (z direction)
        above the table.
        The Box lays on a table, which can be interpreted as x-y plane at z = 0.71. The table starts at x = 0.15 and extends 
        infinite in the positive and negative y direction.
        The starting center position of the box is (0.18, 0.0, 0.82) and the box dimensions are (0.1, 0.30, 0.22). 
        This should be done within 25 seconds
        
        -----Transport rubber tall Box-----
        Pepper should pick up a rubber Box (dimension 0.05, 0.05, 0.1) from its initial center location (0.2, 0.1, 0.75) 
        and place it at (0.2, 0.3, 0.75). The box is positioned on a table, which can be interpreted as x-y plane at z = 0.7. 
        The table starts at x = 0.15 and extends infinite in the positive and negative y direction.
        This should be done within 20 seconds.
        
        -----Transport rubber wide Box-----
        Pepper should pick up a rubber Box (dimension 0.05, 0.1, 0.05) from its initial center location (0.18, 0.1, 0.725) 
        and place it at (0.18, 0.25, 0.725). The box is positioned on a table, which can be interpreted as x-y plane at z = 0.7. 
        The table starts at x = 0.15 and extends infinite in the positive and negative y direction.
        This should be done within 25 seconds.
        
        -----Hand Over 1 RoboHand to another-----
        A rubber box lays on a table, which can be interpreted as x-y plane at z = 0.625. The table starts at x = 0.15 and extends 
        infinite in the positive and negative y direction.
        The starting center position of the box is (0.24, 0.2, 0.675) and the box dimensions are (0.05, 0.05, 0.1). 
        Transport the box to position (0.24, -0.2, 0.675).
        This should be done within 30 seconds
        
        -----Hand Over 1 RoboHand to Human-----
        A rubber box lays on a table, which can be interpreted as x-y plane at z = 0.72. The table starts at x = 0.15 and extends 
        infinite in the positive and negative y direction.
        The starting center position of the box is (0.18, 0.2, 0.77) and the box dimensions are (0.05, 0.05, 0.1). 
        Transport the box and hand it over to me (a person).
        This should be done within 20 seconds
        
        -----Toy panda big pickup-----
        A plush toy panda lays on a table, which can be interpreted as x-y plane at z = 0.70. The table starts at x = 0.15 and extends 
        infinite in the positive and negative y direction.
        The starting center position of the toy panda is (0.2, 0, 0.8) and the toy panda dimensions are (0.20, 0.20, 0.3). 
        Pick up the plush toy panda and lift it 0.1 units, then place it at its initial location again.
        This should be done within 20 seconds
        
        -----Toy panda small pickup-----
        A plush toy panda lays on a table, which can be interpreted as x-y plane at z = 0.70. The table starts at x = 0.15 and extends 
        infinite in the positive and negative y direction.
        The starting center position of the toy panda is (0.18, 0.15, 0.76) and the toy panda dimensions are (0.08, 0.09, 0.12). 
        Pick up the plush toy panda and place it at (0.18, 0.25, 0.76)
        This should be done within 20 seconds
        
        -----sponge wiper-----
        Pick up a sponge on a table and wipe the table.The table can be interpreted as x-y plane at z = 0.71. The table starts at x = 0.15 and extends 
        infinite in the positive and negative y direction.
        The starting center position of the sponge is (0.18, 0.2, 0.76) and the sponge dimensions are (0.12, 0.06, 0.1). 
        The wiping motion should be once to the left (0.1 units) and once to the right(0.1 units).
        This should be done within 20 seconds

        -----scroll Pickup-----
        A document tube stands on a table, which can be interpreted as x-y plane at z = 0.70. The table starts at x = 0.15 and extends 
        infinite in the positive and negative y direction.
        The starting center position of the document tube is (0.18, 0.15, 0.85) and the document tube dimensions are (0.05 diameter and 0.3 tall). 
        Pick up the document tube , turn it 90 degrees and place it on the table lying on its side.
        This should be done within 25 seconds
""")
