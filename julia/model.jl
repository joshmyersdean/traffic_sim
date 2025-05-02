S_TO_IDX = Dict(
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

using POMDPs
import QuickPOMDPs: QuickMDP

# there is 1 car looking to move in each direction and the light is off
initial_state_example = [
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

S_TO_IDX = Dict(
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

m = QuickMDP(
    actions = [
        :north_south_straight,
        :east_west_straight,
        :left_from_north,
        :left_from_south,
        :left_from_east,
        :left_from_west
    ],
    discount = 0.95,
    intialstate = Deterministic(initial_state_example),

    gen = function (s, a, rng)
        # if the light state changes, update the state for the new light state
        # and return without reward
        if a != s[end]
            sp = deepcopy(s)
            sp[end] = a
            return (sp=sp, r=0)
        end

        # if the action does not change the light state, then we will pass 
        # vehicles and calculate reward
        sp = deepcopy(s)

        if a == :north_south_straight
            state_delta = [
                # SN - (priority) send car straight S->N
                (s[S_TO_IDX[:SN]] > 0) ? 1 : 0,
                # SW - (conditional) send car left turn S->W iff N->S and N->W are 0
                (s[S_TO_IDX[:SW]] > 0 && s[S_TO_IDX[:NS]] == 0 && s[S_TO_IDX[:NW]] == 0) ? 1 : 0,
                # SE - (priority) send car right S->E
                (s[S_TO_IDX[:SE]] > 0) ? 1 : 0,
                # NS - (priority) send car straight N->S
                (s[S_TO_IDX[:NS]] > 0) ? 1 : 0,
                # NE - (conditional) send car left turn N->E iff S->N and S->E are 0
                (s[S_TO_IDX[:NE]] > 0 && s[S_TO_IDX[:SN]] == 0 && s[S_TO_IDX[:SE]] == 0) ? 1 : 0,
                # NW - (priority) send car right turn N->W
                (s[S_TO_IDX[:NW]] > 0) ? 1 : 0,
                # WE - (never)
                0,
                # WN - (never)
                0,
                # WS - (conditional) send car right turn W->S iff N->S is 0
                (s[S_TO_IDX[:WS]] > 0 && s[S_TO_IDX[:NS]] == 0) ? 1 : 0,
                # EW - (never)
                0,
                # EN - (conditional) send car right turn E->N iff S->N is 0
                (s[S_TO_IDX[:EN]] > 0 && s[S_TO_IDX[:SN]] == 0) ? 1 : 0,
                # ES - (never)
                0
            ]


        elseif a == :east_west_straight
            state_delta = [
                # SN (never)
                0,
                # SW (never)
                0,
                # SE - (conditional) right turn S->E iff W->E is 0
                (s[S_TO_IDX[:SE]] > 0 && s[S_TO_IDX[:WE]] == 0) ? 1 : 0,
                # NS - (never)
                0,
                # NE - (never)
                0,
                # NW - (conditional) send car right turn N->W if E->W is 0
                (s[S_TO_IDX[:NW]] > 0 && s[S_TO_IDX[:EW]] == 0) ? 1 : 0,
                # WE - (priority) send car straight W->E
                1,
                # WN - send car left turn W->N if E->W and E->N are 0
                (s[S_TO_IDX[:WN]] > 0 && s[S_TO_IDX[:EW]] == 0 && s[S_TO_IDX[:EN]] == 0) ? 1 : 0, 
                # WS - (priority) send car right turn W->S
                (s[S_TO_IDX[:WS]] > 0) ? 1 : 0,
                # EW - (priority) send car straight E->W
                (s[S_TO_IDX[:EW]] > 0) ? 1 : 0,
                # EN - (priority) send car right turn E->N
                (s[S_TO_IDX[:EN]] > 0) ? 1 : 0,
                # ES - (conditional) send car left turn E->S if W->E and W->S are 0
                (s[S_TO_IDX[:ES]] > 0 && s[S_TO_IDX[:WE]] == 0 && s[S_TO_IDX[:WS]] == 0) ? 1 : 0, # 
            ]
        elseif a == :left_from_north
            state_delta = [
                # SN - (never)
                0,
                # SW - (never)
                0,
                # SE - (conditional) right turn if no left turn conflict
                (s[S_TO_IDX[:SE]] > 0 && s[S_TO_IDX[:NE]] == 0) ? 1 : 0,
                # NS - (priority)
                (s[S_TO_IDX[:NS]] > 0) ? 1 : 0,
                # NE - (priority)
                (s[S_TO_IDX[:NE]] > 0) ? 1 : 0,
                # NW - (priority)
                (s[S_TO_IDX[:NW]] > 0) ? 1 : 0,
                # WE - (never)
                0,
                # WN - (never)
                0,
                # WS - (conditional) right turn if no straight conflict
                (s[S_TO_IDX[:WS]] > 0 && s[S_TO_IDX[:NS]] == 0) ? 1 : 0,
                # EW - (never)
                0,
                # EN - (priority)
                (s[S_TO_IDX[:EN]] > 0) ? 1 : 0,
                # ES - (never)
                0
            ]

        elseif a == :left_from_south
            state_delta = [
                # SN - (priority)
                (s[S_TO_IDX[:SN]] > 0) ? 1 : 0,
                # SW - (priority)
                (s[S_TO_IDX[:SW]] > 0) ? 1 : 0,
                # SE - (priority)
                (s[S_TO_IDX[:SE]] > 0) ? 1 : 0,
                # NS - (never)
                0,
                # NE - (never)
                0,
                # NW - (conditional) right turn if no left conflict
                (s[S_TO_IDX[:NW]] > 0 && s[S_TO_IDX[:SW]] == 0) ? 1 : 0,
                # WE - (never)
                0,
                # WN - (never)
                0,
                # WS - (priority)
                (s[S_TO_IDX[:WS]] > 0) ? 1 : 0,
                # EW - (never)
                0,
                # EN - (conditonal) right turn if no straight conflict
                (s[S_TO_IDX[:EN]] > 0 && s[S_TO_IDX[:SN]] == 0) ? 1 : 0,
                # ES - (never)
                0
            ]

        elseif a == :left_from_east
            state_delta = [
                # SN - (never)
                0,
                # SW - (never)
                0,
                # SE - (priority)
                (s[S_TO_IDX[:SE]] > 0) ? 1 : 0,
                # NS - (never)
                0,
                # NE - (never)
                0,
                # NW - (conditional) right turn if no straight conflict
                (s[S_TO_IDX[:NW]] > 0 && s[S_TO_IDX[:EW]] == 0) ? 1 : 0,
                # WE - (never)
                0,
                # WN - (never)
                0,
                # WS - (conditional) right turn if no left conflict
                (s[S_TO_IDX[:WS]] > 0 && s[S_TO_IDX[:ES]] == 0) ? 1 : 0,
                # EW - (priority)
                (s[S_TO_IDX[:EW]] > 0) ? 1 : 0,
                # EN - (priority)
                (s[S_TO_IDX[:EN]] > 0) ? 1 : 0,
                # ES - (priority)
                (s[S_TO_IDX[:ES]] > 0) ? 1 : 0
            ]
        elseif a == :left_from_west
            state_delta = [
                # SN - (never)
                0,
                # SW - (never)
                0,
                # SE - (conditional) right turn if no straight conflict
                (s[S_TO_IDX[:SE]] > 0 && s[S_TO_IDX[:WE]] == 0) ? 1 : 0,
                # NS - (never)
                0,
                # NE - (never)
                0,
                # NW - (priority)
                (s[S_TO_IDX[:NW]] > 0) ? 1 : 0,
                # WE - (priority)
                (s[S_TO_IDX[:WE]] > 0) ? 1 : 0,
                # WN - (priority)
                (s[S_TO_IDX[:WN]] > 0) ? 1 : 0,
                # WS - (priority)
                (s[S_TO_IDX[:WS]] > 0) ? 1 : 0,
                # EW - (never)
                0,
                # EN - (conditional) right turn if no left conflict
                (s[S_TO_IDX[:EN]] > 0 && s[S_TO_IDX[:WN]] == 0) ? 1 : 0,
                # ES - (never)
                0
            ]

        else # this should never happen, off state maybe, so provide no reward
            return (sp=s, r=0)
        end

        # update state
        for i in 1:12
            sp[i] += state_delta[i]
        end

        # this is broken out as a loop in case we want more complex reward logic.
        # For example, if we pass too much from one intersection, the other intersection
        # will have to wait a long time. A decaying reward may be necessary.
        step_reward= 0 # (throughput)
        for i in 1:12
            step_reward += state_delta[i]
        end
        
        # return new state and reward
        return (sp=sp, r=step_reward)
    end,

    # terminal state is no more cars left in any queue
    isterminal = s -> sum(s[1:12]) == 0
)
