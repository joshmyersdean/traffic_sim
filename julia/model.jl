using POMDPs
import QuickPOMDPs: QuickMDP
using POMDPModelTools

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

struct IntersectionState
    car_queue::Vector{Int}
    light_state::Symbol
end

initial_state_example = IntersectionState(
    [1,1,1,1,1,1,1,1,1,1,1,1], 
    :off
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
    initialstate = Deterministic(initial_state_example),

    gen = function (s, a, rng)
        sp = deepcopy(s)

        # if the light state changes, update the state for the new light state
        # and return without reward
        if a !=  s.light_state
            sp.light_state = a
            return (sp=sp, r=0)
        end

        s_cars = s.car_queue

        # if the action does not change the light state, then we will pass 
        # vehicles and calculate reward
        if a == :north_south_straight
            state_delta = [
                # SN - (priority) send car straight S->N
                (s.car_quque[S_TO_IDX[:SN]] > 0) ? 1 : 0,
                # SW - (conditional) send car left turn S->W iff N->S and N->W are 0
                (s.car_quque[S_TO_IDX[:SW]] > 0 && s.car_quque[S_TO_IDX[:NS]] == 0 && s.car_quque[S_TO_IDX[:NW]] == 0) ? 1 : 0,
                # SE - (priority) send car right S->E
                (s.car_quque[S_TO_IDX[:SE]] > 0) ? 1 : 0,
                # NS - (priority) send car straight N->S
                (s.car_quque[S_TO_IDX[:NS]] > 0) ? 1 : 0,
                # NE - (conditional) send car left turn N->E iff S->N and S->E are 0
                (s.car_quque[S_TO_IDX[:NE]] > 0 && s.car_quque[S_TO_IDX[:SN]] == 0 && s.car_quque[S_TO_IDX[:SE]] == 0) ? 1 : 0,
                # NW - (priority) send car right turn N->W
                (s.car_quque[S_TO_IDX[:NW]] > 0) ? 1 : 0,
                # WE - (never)
                0,
                # WN - (never)
                0,
                # WS - (conditional) send car right turn W->S iff N->S is 0
                (s.car_quque[S_TO_IDX[:WS]] > 0 && s.car_quque[S_TO_IDX[:NS]] == 0) ? 1 : 0,
                # EW - (never)
                0,
                # EN - (conditional) send car right turn E->N iff S->N is 0
                (s.car_quque[S_TO_IDX[:EN]] > 0 && s.car_quque[S_TO_IDX[:SN]] == 0) ? 1 : 0,
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
                (s.car_quque[S_TO_IDX[:SE]] > 0 && s.car_quque[S_TO_IDX[:WE]] == 0) ? 1 : 0,
                # NS - (never)
                0,
                # NE - (never)
                0,
                # NW - (conditional) send car right turn N->W if E->W is 0
                (s.car_quque[S_TO_IDX[:NW]] > 0 && s.car_quque[S_TO_IDX[:EW]] == 0) ? 1 : 0,
                # WE - (priority) send car straight W->E
                1,
                # WN - send car left turn W->N if E->W and E->N are 0
                (s.car_quque[S_TO_IDX[:WN]] > 0 && s.car_quque[S_TO_IDX[:EW]] == 0 && s.car_quque[S_TO_IDX[:EN]] == 0) ? 1 : 0, 
                # WS - (priority) send car right turn W->S
                (s.car_quque[S_TO_IDX[:WS]] > 0) ? 1 : 0,
                # EW - (priority) send car straight E->W
                (s.car_quque[S_TO_IDX[:EW]] > 0) ? 1 : 0,
                # EN - (priority) send car right turn E->N
                (s.car_quque[S_TO_IDX[:EN]] > 0) ? 1 : 0,
                # ES - (conditional) send car left turn E->S if W->E and W->S are 0
                (s.car_quque[S_TO_IDX[:ES]] > 0 && s.car_quque[S_TO_IDX[:WE]] == 0 && s.car_quque[S_TO_IDX[:WS]] == 0) ? 1 : 0, # 
            ]
        elseif a == :left_from_north
            state_delta = [
                # SN - (never)
                0,
                # SW - (never)
                0,
                # SE - (conditional) right turn if no left turn conflict
                (s.car_quque[S_TO_IDX[:SE]] > 0 && s.car_quque[S_TO_IDX[:NE]] == 0) ? 1 : 0,
                # NS - (priority)
                (s.car_quque[S_TO_IDX[:NS]] > 0) ? 1 : 0,
                # NE - (priority)
                (s.car_quque[S_TO_IDX[:NE]] > 0) ? 1 : 0,
                # NW - (priority)
                (s.car_quque[S_TO_IDX[:NW]] > 0) ? 1 : 0,
                # WE - (never)
                0,
                # WN - (never)
                0,
                # WS - (conditional) right turn if no straight conflict
                (s.car_quque[S_TO_IDX[:WS]] > 0 && s.car_quque[S_TO_IDX[:NS]] == 0) ? 1 : 0,
                # EW - (never)
                0,
                # EN - (priority)
                (s.car_quque[S_TO_IDX[:EN]] > 0) ? 1 : 0,
                # ES - (never)
                0
            ]

        elseif a == :left_from_south
            state_delta = [
                # SN - (priority)
                (s.car_quque[S_TO_IDX[:SN]] > 0) ? 1 : 0,
                # SW - (priority)
                (s.car_quque[S_TO_IDX[:SW]] > 0) ? 1 : 0,
                # SE - (priority)
                (s.car_quque[S_TO_IDX[:SE]] > 0) ? 1 : 0,
                # NS - (never)
                0,
                # NE - (never)
                0,
                # NW - (conditional) right turn if no left conflict
                (s.car_quque[S_TO_IDX[:NW]] > 0 && s.car_quque[S_TO_IDX[:SW]] == 0) ? 1 : 0,
                # WE - (never)
                0,
                # WN - (never)
                0,
                # WS - (priority)
                (s.car_quque[S_TO_IDX[:WS]] > 0) ? 1 : 0,
                # EW - (never)
                0,
                # EN - (conditonal) right turn if no straight conflict
                (s.car_quque[S_TO_IDX[:EN]] > 0 && s.car_quque[S_TO_IDX[:SN]] == 0) ? 1 : 0,
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
                (s.car_quque[S_TO_IDX[:SE]] > 0) ? 1 : 0,
                # NS - (never)
                0,
                # NE - (never)
                0,
                # NW - (conditional) right turn if no straight conflict
                (s.car_quque[S_TO_IDX[:NW]] > 0 && s.car_quque[S_TO_IDX[:EW]] == 0) ? 1 : 0,
                # WE - (never)
                0,
                # WN - (never)
                0,
                # WS - (conditional) right turn if no left conflict
                (s.car_quque[S_TO_IDX[:WS]] > 0 && s.car_quque[S_TO_IDX[:ES]] == 0) ? 1 : 0,
                # EW - (priority)
                (s.car_quque[S_TO_IDX[:EW]] > 0) ? 1 : 0,
                # EN - (priority)
                (s.car_quque[S_TO_IDX[:EN]] > 0) ? 1 : 0,
                # ES - (priority)
                (s.car_quque[S_TO_IDX[:ES]] > 0) ? 1 : 0
            ]
        elseif a == :left_from_west
            state_delta = [
                # SN - (never)
                0,
                # SW - (never)
                0,
                # SE - (conditional) right turn if no straight conflict
                (s.car_quque[S_TO_IDX[:SE]] > 0 && s.car_quque[S_TO_IDX[:WE]] == 0) ? 1 : 0,
                # NS - (never)
                0,
                # NE - (never)
                0,
                # NW - (priority)
                (s.car_quque[S_TO_IDX[:NW]] > 0) ? 1 : 0,
                # WE - (priority)
                (s.car_quque[S_TO_IDX[:WE]] > 0) ? 1 : 0,
                # WN - (priority)
                (s.car_quque[S_TO_IDX[:WN]] > 0) ? 1 : 0,
                # WS - (priority)
                (s.car_quque[S_TO_IDX[:WS]] > 0) ? 1 : 0,
                # EW - (never)
                0,
                # EN - (conditional) right turn if no left conflict
                (s.car_quque[S_TO_IDX[:EN]] > 0 && s.car_quque[S_TO_IDX[:WN]] == 0) ? 1 : 0,
                # ES - (never)
                0
            ]

        else # this should never happen, off state maybe, so provide no reward
            return (sp=s, r=0)
        end

        # this is broken out as a loop in case we want more complex reward logic.
        # For example, if we pass too much from one intersection, the other intersection
        # will have to wait a long time. A decaying reward may be necessary.
        step_reward= 0 # (throughput)
        for i in 1:12
            step_reward += state_delta[i]
        end

        sp = IntersectionState(s.car_queue - state_delta, s.light_state)
        
        # return new state and reward
        return (sp=sp, r=step_reward)
    end,

    # terminal state is no more cars left in any queue
    isterminal = s -> sum(s.car_queue) == 0,
    statetype = IntersectionState,
)