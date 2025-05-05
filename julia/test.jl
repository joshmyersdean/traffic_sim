using POMDPs
using QuickPOMDPs
using POMDPTools
using MCTS
using DataFrames

include("model.jl")

using .IntersectionModel

# policy = RandomPolicy(m)

struct MyDeterministicPolicy <: Policy
    # include parameters or mappings if needed
end

function POMDPs.action(policy::MyDeterministicPolicy, s)
    # choose existing action 80% of the time; otherwise choose a random action
    if rand() > 0.5
        return s.light_state
    else
        return rand(actions(m))
    end
end

println("Using deterministic policy...")
policy = MyDeterministicPolicy()

initial_state = IntersectionState(
    fill(5, 12), 
    :off
)

hr = HistoryRecorder(max_steps=100)
history = simulate(hr, m, policy, initial_state)
# @show history

function history_to_dataframe(history)
    return DataFrame(
        CarsState = [h[1].car_queue for h in history],
        LightState = [h[1].light_state for h in history],
        Action = [h[2] for h in history],
        NextCarsState = [h[3].car_queue for h in history],
        NextLightState = [h[3].light_state for h in history],
        Reward = [h[4] for h in history],
        TimeStep = [h[6] for h in history]
    )
end

df = history_to_dataframe(history)
show(df, allrows=true, allcols=true)

println()

total_reward = sum([h[4] for h in history])
@show total_reward

println("Using MCTS...")
solver = MCTSSolver(n_iterations=10_000, depth=40, exploration_constant=5.0)
planner = solve(solver, m)

hr = HistoryRecorder(max_steps=100)

initial_state = IntersectionState(
    fill(5, 12), 
    :off
)

history = simulate(hr, m, planner, initial_state)

function history_to_dataframe(history)
    return DataFrame(
        CarsState = [h[1].car_queue for h in history],
        LightState = [h[1].light_state for h in history],
        Action = [h[2] for h in history],
        NextCarsState = [h[3].car_queue for h in history],
        NextLightState = [h[3].light_state for h in history],
        Reward = [h[4] for h in history],
        TimeStep = [h[6] for h in history]
    )
end

df = history_to_dataframe(history)
show(df, allrows=true, allcols=true)

println()

total_reward = sum([h[4] for h in history])
@show total_reward