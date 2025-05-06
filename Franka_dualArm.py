Prompt = (
    """
    
    Introduction: 
You control a pair of Franka Emika Panda 7-DOF robotic arms. 
Your goal is to generate a MATLAB file called x_d.m that, when run, produces a file x_d.mat containing 7 variables based 
on the USER COMMAND at the end of the prompt. 
The generated trajectories must adhere to the workspace and collision constraints, maintain smoothness, and respect the provided timeframe.

    ___________________________________________________________________________________________________________________
    ENVIRONMENT SET-UP:
        Coordinate System:
            1.	x-axis: depth, increasing away from you.
            2.	y-axis: horizontal, increasing to the left.
            3.	z-axis: vertical, increasing upwards.
        The robot arm bases are located at the locations:
            Base 1: (x = 0, y = 0.4, z = 0)
            Base 2: (x =0, y = -0.4, z = 0)
        Ground plane = x-y plane at z = 0
        The top part of the robots end-effectors are currently positioned at
            End effector 1:  (x = 0.31, y = 0.4, z = 0.59), rotation around z = 0
            End effector 2:  (x = 0.31, y = -0.4, z = 0.59), rotation around z = 0
        End Effector Interaction Plate:
            1.	Plate center at end-effector tool center.
            2.	End effector plate dimensions:
                i.	Length (x-direction): 0.2 (±0.1 from the center)
                ii.	Thickness (y-direction): 0.03 (±0.015 from the center)
                iii. Depth (z-direction): -0.077 (downwards)
            3.	Rotation around z: ±pi radians. Negative = clockwise, positive = anticlockwise.
            4.	Initial orientation: Plate long side parallel to x-axis. 
                Interactions (push/lift) must use a plate’s long side (the 0.2 side) aligned appropriately to the target object’s surface.
                Therefore the plates are initially aligned to clamp a box along the y-axis and must rotate +-pi/2 to clamp along the x-axis.
            5.	The robot arms are top-down, facing the tabletop.
    ___________________________________________________________________________________________________________________
    WORKSPACE CONSTRAINTS:
    The motion must remain within the following workspace boundaries:
        global coordinate system:
            Arm1 - tool center point 1:
                1.	x-axis: [0.0, 0.5]
                2.	y-axis: [-0.2, 0.9]
                3.	z-axis: [0.0, 0.7]
            Arm2 - tool center point 2:
                1.	x-axis: [0.0, 0.5]
                2.	y-axis: [-0.9, 0.2]
                3.	z-axis: [0.0, 0.7]
    
        Do not exceed these limits at any time.
    ___________________________________________________________________________________________________________________
    COLLISION AVOIDANCE:
        1.	Consider object and end-effector plate dimensions.
        2.	Avoid collisions between the two end effectors.
        3.	Account for plate dimensions! If you want to interact with objects, you have to account for the 0.030 (+- 0.015) 
            thick interaction plate!
        4.  When picking up objects, always approach from the sides! Approaching from above with aligned plates can lead to 
            collision with the top.
        5. Do not collide with the ground plane! There should always be at least z = 0.01 units between end effector (or plate) 
            and ground plane, unless the User command demands interaction with the ground plane!
        6. Make sure to avoid crashing into objects you have just moved and remember the new position of moved objects
    ___________________________________________________________________________________________________________________
    TRAJECTORY GENERATION:
        1.	Break down the trajectories for both arms into defined phases 
            (e.g., “Approach with Arm1,” “Interact with Arm1,” “Approach with Arm2,” “Retreat Arm1,” etc.).
        2.	Assign time to each phase, generate the required number of waypoints, and ensure smooth continuity 
            (the end point of one step is the start of the next).
        3.	If the task involves interacting with a specific object part, identify which side is best to engage.
        4.  After finishing the task return to the initial position.
    ___________________________________________________________________________________________________________________
    TIME DISCRETIZATION:
            Time is discretized in 0.001-second intervals (1 ms time steps), i.e., 1000 steps per second.
    ___________________________________________________________________________________________________________________
    OUTPUT DATA FORMAT:
        The final output should be matlab file called “x_d.m” containing code that generates exactly 7 variables: 
        time, position1 , position2, K_matrix1, K_matrix2, coupling_vector and rot_z
        1.	time: (time/timesteps+1)x1 vector, Absolute time in seconds.
        2.	position1: (time/timesteps+1)x3 matrix, 
            i.	x, y, z positions of the end-effector of Arm 1 at each time step.
        3.	position2: (time/timesteps+1)x3 matrix, 
            i.	x, y, z positions of the end-effector of Arm 2 at each time step.
        4.	K_matrix1: (time/timesteps+1)x4 vector, Desired Cartesian stiffness of the end-effector of Arm 1
        5.	K_matrix2: (time/timesteps+1)x4 vector, Desired Cartesian stiffness of the end-effector of Arm 2
        6.	coupling_vector: (time/timesteps+1)x5 vector. [coupling on/off (1/0), coupling stiffness, clamp_distance_x, clamp_distance_y, clamp_distance_z].
        7.	rot_z: (time/timesteps+1)x2 vector [Left z_rot, Right z_rot], in radiant.
    
        The values should be stored as float64.
    ___________________________________________________________________________________________________________________
    STIFFNESS MATRIX:
        1.  Define the variables K_matrix = [Kx, Ky, Kz, Krot] for a Cartesian stiffness matrix diag(Kx, Ky, Kz, Krot, Krot, Krot) for the end-effector. The stiffness values change 
        based on environmental interaction, provided in the user prompt. The rotational stiffness Krot should be equal to the largest stiffness value among [Kx, Ky, Kz].
        Kx, Ky and Kz can differ depending on the expected interaction direction, (e.g. if interaction forces are only expected in z-direction, lower the stiffness Kz)
        In the description below you will find typical reference values for a stiffness K:
            1.1. High Stiffness (K ≈ 10000.0): No contact (free space).
            1.2. Medium Stiffness (K ≈ 5000.0): Contact with low-stiffness environment. (e.g. soft ball)
            1.3. Low Stiffness (K ≈ 1000.0): Contact with a stiff environment. (e.g. wooden tabletop)
        2.  Adjust stiffness if the robotic arm comes into contact with the environment 
            (e.g., reduce stiffness when contacting a stiff surface like a table).  
        3.  Once the two arms are coupled, treat stiffness as follows.
            3.1 The clamping (spring) axis always stays soft: K = 100.
            3.2 Of the two remaining axes, only the one in which the tool-centre actually moves during the current phase is softened 
                to Medium (~5000); the other stays High (~10000).
            3.3 Rotational stiffness Krot is always set to the largest of Kx, Ky, Kz.
        4.	Expected transitions would be for example: “Approaching with high stiffness in free space, medium stiffness 
            when contacting a rubber box, low stiffness when touching and gliding along a wooden table”.
    ___________________________________________________________________________________________________________________
    COUPLING VECTOR:
        1. Coupling activates a virtual spring between the two arms to pick up objects.
        2. coupling_vector(1) = 1 or 0 (on/off)
        3. coupling_vector(2) = coupling stiffness Kc
        4. coupling_vector(3:5) = [clamp_distance_x, clamp_distance_y, clamp_distance_z]
        5. With clamp_distance you can chose the direction of clamping. Set the clamp_distance equal to the object width which is clamped.
           The other clamp_distance values must remain 0.
        6. You must estimate the objects approximate weight (if not provided) and its object-stiffness. Then choose an appropriate
           stiffness Kc. You are not bound to the exact example values of Kc, you can choose values between them.
        7. material examples: (cardboard box = light and 6000 stiffness); (hollow wood box = middle_weight and 50000 stiffness); 
           (hardwood box = heavy and 75000)
        8. example values:
        "light = ~0.04kg": [{ "object stiffness": 1000,  "Kc": 120 },
                { "object stiffness": 6000,  "Kc": 100 },
                { "object stiffness": 10000, "Kc": 120 },
                { "object stiffness": 50000, "Kc": 230 },
                { "object stiffness": 100000,"Kc": 295 }],
        "middle_weight = ~0.1kg": [{ "object stiffness": 1000,  "Kc": 260 },
                { "object stiffness": 10000, "Kc": 310 },
                { "object stiffness": 50000, "Kc": 910 },
                { "object stiffness": 100000,"Kc": 1489 }],
        "heavy = ~1kg": [{ "object stiffness": 50000,  "Kc": 650 },
                { "object stiffness": 100000, "Kc": 400 }]
        9. Lower the corresponding value of the STIFFNESS MATRIX (Kx or Ky or Kz) to 100 to avoid counteraction
        

    ___________________________________________________________________________________________________________________
    OBJECT INTERACTION:
        1.	To properly interact with objects along a certain side, you must rotate the end effector around the z-axis so 
            that the long side of the interaction plate is oriented towards the object’s surface. For example:
            i.	If you need to push or hold the object along the object’s x-axis dimension 
                (approaching it from the “left” or “right” side), rotate the end effector’s plate by ±0° (±0 radians) 
                around the z-axis so that the long side of the plate aligns with the object’s x-axis.
        2.	When interacting (pushing, grasping) with an object, always account for end effector / interaction plate 
            dimensions to avoid overlapping/collision.
            i.	For example: If the box is 0.1 units wide in the direction you are pushing from, 
                and each end-effector plate protrudes 0.015 units from the tool center in that direction , 
                then the two tool centers (for Arm1 and Arm2) must be separated by: 2 x 0.015 + 0.1 = 0.13 units total
        3. Try to maximize gripping surface
        4. When grasping, arms must maintain contact and coupling with the box from the moment they first engage it 
           until the box is fully placed at the final position. Only after the box has been placed at its final 
           position and is securely resting on the target surface may the arms disengage
        5. If the USER COMMAND violates the workspace constraints of one arm, consider splitting the task in two sub tasks using both arms.
        6. Interpolate the rot_z values to avoid jumps in orientation.
        7. You can use a single Arm to push objects or two arms (dual arm) to grasp and pick up objects.
        8. Just before touching an object, the end effector velocity must be low to avoid large contact forces.
        9. You can not position the end effector centers lower than the highest point of an object. This avoids collision between end effector and object.

    SINGLE ARM REQUIREMENTS
        1. You can only push objects, you cannot pick them up with one arm.

    DUAL ARM REQUIREMENTS
        1. When approaching objects, you must align and position the interaction plates, leaving a safety 0.05-unit 
           lateral offset between each plate and the object. Hold this position for 0.5 s, then move laterally to grasp.
        2. After grasping, hold the grasp for 0.5 s before lifting the object.
        2. When releasing the object, move away laterally at least 0.05 units, then continue.
          	
    ___________________________________________________________________________________________________________________
    ADDITIONAL REQUIREMENTS:
        1.  If one Arm is not used for a subtask, retreat 
            it if it is in the way of the other Arm or let it stay at the current position if there is no risk of collision.
        2.  Check at every step if the Workspace constraints are met.
        3.  Pushing objects might lead to inaccurate object locations. Therefore only push objects in a straight line, engaging at 
            the center of the respective side
        4.  At the end, verify that all output variables have the correct shape
        5.  Important: You can only lower the interaction plates until the center of the end effector aligns with the highest point of the object.
            Only the interaction plate can make contact with an object.
        6.  Demands from the User Command are prioritized over constraints in the prompt.
    ___________________________________________________________________________________________________________________
    OUTPUT
        Your output should be:
        1. A step by step explanation that includes:
            1.1  short Phase description (e.g., “Approach,” “Contact and Push,” “Lift,” “Transfer,” “Retreat”)
            1.2  Relevant variables (K_matrix1, K_matrix2, coupling_vector, rot_z) for that phase
            1.3  Description which arm is necessary for phase
            1.4. the necessary waypoints
            1.5. timestamps 
            1.6. Analysis of objects that are relevant in collision avoidance
        
        2. Matlab code that, if run, will produce x_d.mat with the specified variables and format.
        Make sure that the variables time, K_matrix1, K_matrix2, position1, position2, coupling_vector, rot_z have the correct format.
     ___________________________________________________________________________________________________________________
    USER COMMAND: 
        Define a trajectory for each of the two robot arms to wipe the ground surface with a sponge. The starting center position of the sponge is (0.35, 0.0, 0.05) 
        and the sponge dimensions are (0.1, 0.1, 0.1).
        Timeframe = maximum 25 seconds.
    
    
    """
)


USER_COMMAND_LIST = (
    """
---------------- pick and place CARDBOARD box ------------------------
        Define a trajectory for each of the two robot arms, that carry a cardboard box from its starting position to an 
        end position. At some point the box should be at least 0.2 units above the ground.
        The starting center position of the box is (0.3, 0.25, 0.05) and the box dimensions are (0.1, 0.1, 0.1).
        The end center position of the box is (0.3, - 0.25, 0.05) Timeframe = 15 seconds.

---------------- pick and place HARDWOOD box ------------------------
        Define a trajectory for each of the two robot arms, that carry a hardwood box from its starting position to an 
        end position. At some point the box should be at least 0.2 units above the ground.
        The starting center position of the box is (0.35, 0.0, 0.05) and the box dimensions are (0.1, 0.1, 0.1).
        The end center position of the box is (0.05, 0.0, 0.05) Timeframe = 15 seconds.

---------------- hand over pick and place cardboard box----------------------------
        Define a trajectory for each of the two robot arms, that transport a cardboard box from its starting position to an 
        end position. At some point the box should be at least 0.2 units above the ground.
        The starting center position of the box is (0.3, 0.5, 0.05) and the box dimensions are (0.1, 0.1, 0.1).
        The end center position of the box is (0.3, - 0.25, 0.05) Timeframe = 20 seconds.

---------------- stack CARDBOARD boxes ------------------------
        Define a trajectory for each of the two robot arms, that carry a cardboard box from its starting position to an 
        end position. At some point the box should be at least 0.2 units above the ground.
        The starting center position of the box is (0.35, 0.0, 0.05) and the box dimensions are (0.1, 0.1, 0.1).
        The end center position of the box is (0.05, 0.0, 0.05) Timeframe = 15 seconds.

---------------- Wipe with sponge ------------------------
        Define a trajectory for each of the two robot arms to wipe the ground surface with a sponge. The starting center position of the sponge is (0.35, 0.0, 0.05) 
        and the sponge dimensions are (0.1, 0.1, 0.1).
        Timeframe = maximum 25 seconds.

    """
)
