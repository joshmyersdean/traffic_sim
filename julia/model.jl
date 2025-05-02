lane_to_state_index = Dict(
    :SN => 1,
    :SW => 2,
    :SE => 3,
    :NS => 4,
    :NE => 5,
    :NW => 6,
    :WE => 7,
    :WN => 8,
    :WS => 9,
    :EW => 10,
    :EN => 11,
    :ES => 12
)

TRAFFIC_LIGHT_STATES = [
    :north_south_straight, # north to south, south to north; both straight
    :east_west_straight, # east to west, west to east; both straight
    :left_from_north,
    :left_from_south,
    :left_from_east,
    :left_from_west,
    :off
]

# it will be important to turn these into a generative function
ALLOWED_TRANSITIONS = Dict(
    :north_south_straight => [:NS, :SN, :NW, :SE],  # straight flow from north and south
    # :WS if :NS == 0 (right turn if nobody is going straight)
    # :SW if :NS == 0 AND :NW == 0 (left turn if nobody is going straight or right)
    # :EN if :SN == 0 (right turn if nobody is going straight)
    # :NE if :SN == 0 AND :SE == 0 (left turn if nobody is going straight or right)
    :east_west_straight => [:EW, :WE, :EN, :WS],    # straight flow from east and west
    # :NW if :EW == 0 (right turn if nobody is going straight)
    # :WN if :EW == 0 AND :EN == 0 (left turn if nobody is going straight or right)
    # :SE if :WE == 0 (right turn if nobody is going straight)
    # :ES if :WE == 0 AND :WS == 0 (left turn if nobody is going straight or right)
    :left_from_north => [:NE, :NS, :NW, :EN],   # full flow from north and right 
                                                # turn from east because it is 
                                                # shielded by the left turn arrow
    # :WS if :NS == 0
    # :SE if :NE == 0
    :left_from_south => [:SW, :SN, :SE, :WS],   # full flow from south and right
                                                # turn from west because it is 
                                                # shielded by the left turn arrow
    # :NW if :SW == 0
    # :EN if :SN == 0
    :left_from_east => [:ES, :EW, :EN, :SE],    # full flow from east and right 
                                                # turn from south because it is 
                                                # shielded by the left turn arrow
    # :WS if :ES == 0
    # :NW if :EW == 0
    :left_from_west => [:WN, :WE, :WS, :NW],    # full flow from west and right 
                                                # turn from north because it is 
                                                # shielded by the left turn arrow
    # :EN if :WN == 0
    # :SE if :WE == 0
    :off => []  # nobody is allowed to move
)

ACTIONS = [
    :north_south_straight,
    :east_west_straight,
    :left_from_north,
    :left_from_south,
    :left_from_east,
    :left_from_west
]
# If the action does not equal the state vector index, it is a transition and 
# no reward is given. If it does equal the index, then cars are passed and a 
# reward is given based on the number of cars passed.

# there is 1 car looking to move in each direction and the light is off
state_example = [
    1, # NS
    1, # SN
    1, # SW
    1, # SE
    1, # NS
    1, # NE
    1, # NW
    1, # WE
    1, # WN
    1, # WS
    1, # EW
    1, # EN
    1, # ES
    :off # final state is light state
]

# possible terminal state is no cars (array empty)