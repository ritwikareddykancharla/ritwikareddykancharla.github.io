"""Trainium, Kaggriculture, CUDA and routing project pages. Facts come from the project repos and run ledgers."""

CHART = """<svg viewBox="0 0 860 300" role="img" aria-label="Validation bits per byte at five checkpoints, falling from 1.3951 to 0.9656">
<g stroke="var(--chart-grid)" stroke-width="1"><line x1="60" y1="40" x2="820" y2="40"/><line x1="60" y1="110" x2="820" y2="110"/><line x1="60" y1="180" x2="820" y2="180"/><line x1="60" y1="250" x2="820" y2="250"/></g>
<g font-family="var(--mono)" font-size="12" fill="var(--chart-text)"><text x="14" y="44">1.40</text><text x="14" y="114">1.25</text><text x="14" y="184">1.10</text><text x="14" y="254">0.95</text><text x="86" y="284">initial</text><text x="240" y="284">submission 5</text><text x="446" y="284">D62</text><text x="626" y="284">D70</text><text x="776" y="284">D72</text></g>
<path d="M110,42 L280,234 L460,242 L640,242 L790,243 L790,250 L110,250 Z" fill="var(--chart-fill)"/>
<polyline points="110,42 280,234 460,242 640,242 790,243" fill="none" stroke="var(--chart-line)" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>
<g fill="var(--chart-dot)" stroke="var(--chart-line)" stroke-width="3"><circle cx="110" cy="42" r="6"/><circle cx="280" cy="234" r="6"/><circle cx="460" cy="242" r="6"/><circle cx="640" cy="242" r="6"/><circle cx="790" cy="243" r="6"/></g>
<g font-family="var(--mono)" font-size="13" fill="var(--chart-label)"><text x="126" y="46">1.3951</text><text x="296" y="222">0.9848</text><text x="766" y="226">0.9656</text></g></svg>"""

# =============================================================================== Trainium
TRAINIUM = dict(
    hero=dict(img="surfers", accent="#12737a", alt="Surfers on coloured boards seen from directly above, spread across calm teal water."),
    title="Model and Kernel Co-Design under a 30-Minute Training Budget | Ritwika Kancharla",
    description="AWS Trainium Frontier: validation bits per byte reduced from 1.3951 to 0.9656 within a fixed 30-minute training budget through joint changes to the architecture and the kernels.",
    eyebrow="AWS Trainium Frontier, 2026",
    h1="Model and Kernel Co-Design under a 30-Minute Training Budget",
    meta=["Ritwika Kancharla", "September 2026"],
    links=[("Challenge", "https://trainium-frontier.devpost.com/")],
    abstract="""<p>The AWS Trainium Frontier challenge fixes the hardware (AWS Trainium2), the dataset and the wall-clock time. Entries are ranked by the validation bits per byte of the language model that exists when 30 minutes of training have elapsed. Under this rule the number of optimizer steps is not fixed, so each design decision affects both how much the model learns per step and how many steps fit in the budget.</p>
<p>This project reduced validation bits per byte from 1.3951 to 0.9656 in full-budget local runs. The best submitted model scored 0.9848 and held first place on the public leaderboard at its peak. Most of the improvement came from two changes that depend on each other: a wider and shallower model, and hand-fused kernels that shorten each training step. Several modifications that improved loss at a fixed step count produced a worse final model, and these negative results are reported.</p>""",
    body=f"""
    <h2 id="problem">Problem statement</h2>
    <p>The usual comparison between training recipes asks which one reaches the lowest loss after a fixed number of steps. Here the fixed quantity is time. A modification that lowers the loss at step 1,000 can still lose if it adds 20 ms to every step, because the run ends before the step at which the modification would have paid off. The objective is therefore the validation loss at the end of a complete 30-minute run, measured through the official scoring path. Short runs were used only to reject clearly unsuccessful ideas.</p>

    <h2 id="method">Experimental protocol</h2>
    <ol>
      <li>Profile one training step and attribute its time to operators.</li>
      <li>Change one thing, either the architecture or the system, and never both in the same experiment.</li>
      <li>Run a short gate that checks loss and throughput.</li>
      <li>If the change passes the gate, run the full 30 minutes. Only this result is recorded as the outcome.</li>
      <li>Build the submission artifact and confirm that its score matches the local run.</li>
    </ol>
    <p>Every run was recorded in a ledger with its architecture, batch size, optimizer settings, kernel set, seconds per step, steps completed and final score. Kernels were first developed as isolated microbenchmarks and were always measured again inside the full trainer, because an operator that is faster in isolation can still increase step time once synchronisation and host overhead are included.</p>

    <h2 id="config">Final configuration</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Aspect</th><th>Choice</th></tr></thead>
      <tbody>
        <tr><td>Model</td><td>Width of about 1024, eight layers, attention in a subset of layers, U-Net-style skip connections</td></tr>
        <tr><td>Parallelism</td><td>Four processes, 262k tokens per effective batch</td></tr>
        <tr><td>Optimizers</td><td>Muon for the large matrices; AdamW for embeddings, the output head and small parameters; warmup and cooldown set to the number of steps that fit</td></tr>
        <tr><td>Precision</td><td>BF16 state; FP8 on the projection paths where the numerical error remained acceptable</td></tr>
        <tr><td>Fused kernels</td><td>Normalisation, RoPE, cross entropy, ReLU&sup2;, flash attention, embedding scatter and parts of the optimizer step, written against the AWS Neuron Kernel Interface</td></tr>
        <tr><td>Launch overhead</td><td>Small table preparations batched; residual operations fused where an end-to-end profile showed a benefit</td></tr>
      </tbody>
    </table></div>

    <h2 id="results">Results</h2>
    <figure class="fig"><div class="plate">{CHART}</div>
    <figcaption><b>Figure 1.</b> Validation bits per byte at each checkpoint (lower is better). Nearly all of the improvement comes from the first change to the architecture together with the first fused kernels.</figcaption></figure>
    <div class="tablewrap"><table>
      <thead><tr><th>Checkpoint</th><th class="r">val bpb</th><th>Change</th><th>Measurement</th></tr></thead>
      <tbody>
        <tr><td>Initial submission</td><td class="r">1.3951</td><td>Reference recipe</td><td>Starting point</td></tr>
        <tr><td>Submission 5</td><td class="r">0.9848</td><td>Wider and shallower model, first fused kernels</td><td>Leaderboard; first place at its peak</td></tr>
        <tr><td>D62</td><td class="r">0.9679</td><td>Embedding scatter kernel, batched Muon tail</td><td>Local</td></tr>
        <tr><td>D70</td><td class="r">0.9669</td><td>FP8 projection path</td><td>Local</td></tr>
        <tr class="best"><td>D72</td><td class="r">0.9656</td><td>Batched FP8 tables, fused RoPE</td><td>Local</td></tr>
      </tbody>
    </table></div>
    <div class="note"><b>Measurement</b><p>Local validation, the built artifact and the public leaderboard are three different measurements. Packaging and runtime differences produced measurable offsets between them, so they are reported separately.</p></div>

    <h2 id="negative">Negative results</h2>
    <h3>A faster kernel that slowed the trainer</h3>
    <p>A BF16 matrix-multiplication kernel that kept weights resident was 6 to 18% faster than the stock operator in microbenchmarks. Inside the trainer it increased step time from about 0.715 s to 0.870 s, because synchronisation and integration costs exceeded the saving.</p>
    <h3>Gating improved loss per step and reduced the number of steps</h3>
    <p>Attention gates and smear gates gave the best loss at a matched step count. They also added enough small operations per step that the run completed fewer updates and ended with a worse model. Moving the multiplications into kernels did not recover the loss, because slicing small gate inputs and launching many small operations consumed the gain.</p>
    <h3>More capacity, worse final model</h3>
    <p>A 203M-parameter model with value embeddings learned faster per step, completed 11% fewer steps and finished behind. A ten-layer model showed the same pattern.</p>
    <h3>Packaging errors</h3>
    <p>One built candidate ran 7% slower because the builder omitted a flash-attention flag. An earlier artifact passed locally and failed in the scorer because a module alias recursed and fell back without reporting an error. The submission builder now has its own parity tests.</p>

    <h2 id="conclusions">Conclusions</h2>
    <ul>
      <li>Under a time budget, the quantity to optimise is the score at the end of the budget. Proxies at a fixed step count are misleading.</li>
      <li>Learning per step and time per step must be reported together for every experiment.</li>
      <li>An end-to-end profile of the trainer is more reliable than any microbenchmark.</li>
      <li>The code that builds the submission requires the same testing as the training code.</li>
    </ul>
""",
)

# =============================================================================== Kaggriculture
KAGG = dict(
    hero=dict(img="tulips", accent="#c4356a", pos="50% 70%", alt="A field of pink tulips in front of sunlit, glittering water."),
    title="Imitation Learning for a Long-Horizon Economic Game | Ritwika Kancharla",
    description="Kaggriculture: recurrent behaviour cloning on 100,660 expert decisions, a strict evaluation audit that exposed 30 invalid games, and a curriculum for reinforcement learning.",
    eyebrow="Kaggle simulation, ongoing",
    h1="Imitation Learning for a Long-Horizon Economic Game",
    meta=["Ritwika Kancharla", "September 2026", "Work in progress"],
    links=[("Competition", "https://www.kaggle.com/competitions/kaggriculture")],
    abstract="""<p>Kaggriculture is a two-player farming economy hosted on Kaggle. A full game consists of about 719 decisions in which each player buys land, plants, processes, transports and sells in a market shared with the opponent. This project trains a recurrent policy by behaviour cloning on 140 complete games (100,660 decisions) played by two scripted agents, <code>Pipe7</code> and <code>V47</code>.</p>
<p>The learned policy is not yet competitive. The main contribution so far is methodological. The game engine reports a match as completed even when an agent raised an error during play, so the first evaluation overstated performance. A stricter audit of 96 games found 30 invalid games, all caused by a single input-encoding limit, and no wins against either scripted agent. My best leaderboard score, 2,562.9, comes from a scripted agent and not from the learned policy.</p>""",
    body="""
    <h2 id="problem">Problem statement</h2>
    <p>Rewards in this game are delayed and depend on chains of actions. Buying land is useful only if labour, seed, processing, transport and demand all become available before day 29. The opponent changes prices and the set of reachable options. An apparently idle move can be correct because it preserves cash for a more valuable chain two days later.</p>
    <p>A scripted agent can execute one coherent plan very well. It cannot recover when the opponent, or its own earlier error, moves the game into a state the plan did not anticipate. The aim of this project is a learned agent that can.</p>

    <h2 id="data">Data</h2>
    <p>Games were generated by running <code>Pipe7</code> and <code>V47</code> across seeds, both seats and several opponents. Each game is stored as one ordered sequence, together with the engine version, the opponent, the final cash and a hash that allows exact replay.</p>
    <div class="tablewrap"><table>
      <thead><tr><th>Corpus</th><th class="r">Value</th></tr></thead>
      <tbody>
        <tr><td>Complete games</td><td class="r">140</td></tr>
        <tr><td>Expert decisions</td><td class="r">100,660</td></tr>
        <tr><td>Decisions per game</td><td class="r">719</td></tr>
        <tr><td>Seeds shared between training and test splits</td><td class="r">0</td></tr>
      </tbody>
    </table></div>

    <h2 id="approach">Approach</h2>
    <p>The policy is a recurrent network trained to predict the expert's action at each decision. When training on a later segment of a game, the earlier segment is first replayed through the network so that its hidden state matches the state it would have at that point in a real game. Without this step, the model is asked to predict day 20 from a memory that has not observed days 0 to 19, and it learns an inconsistent mapping.</p>

    <h2 id="evaluation">Evaluation audit</h2>
    <p>One checkpoint was evaluated on 16 unseen seeds, in both seats, against three opponents, for a total of 96 games. The first summary appeared acceptable. The engine, however, marks a match as <code>DONE</code> even if an agent raised an error partway through. A second evaluator was written that checks every status and confirms that the agent was called at every decision.</p>
    <div class="tablewrap"><table>
      <thead><tr><th>Opponent</th><th class="r">Games</th><th class="r">Valid wins</th><th class="r">Valid losses</th><th class="r">Invalid (agent error)</th></tr></thead>
      <tbody>
        <tr><td>Wheat baseline</td><td class="r">32</td><td class="r">28</td><td class="r">0</td><td class="r">4</td></tr>
        <tr><td><code>Pipe7</code></td><td class="r">32</td><td class="r">0</td><td class="r">18</td><td class="r">14</td></tr>
        <tr><td><code>V47</code></td><td class="r">32</td><td class="r">0</td><td class="r">20</td><td class="r">12</td></tr>
        <tr class="best"><td>Total</td><td class="r">96</td><td class="r">28</td><td class="r">38</td><td class="r">30</td></tr>
      </tbody>
    </table></div>
    <div class="note"><b>Scope</b><p>These figures describe one behaviour-cloning checkpoint and are not my best competition result. For reference, <code>V47</code> beat <code>Pipe7</code> in 30 of 40 recorded games.</p></div>

    <h2 id="findings">Findings</h2>
    <h3>An encoding limit appeared as poor strategy</h3>
    <p>All 30 invalid games failed immediately after the farm grew beyond 16 active units. The policy input has room for 16 units and the game permits more. Clipping the input would have hidden the defect, so the input format must be extended and the 30 games remain marked as invalid.</p>
    <h3>The policy generalised only to the opponent seen in training</h3>
    <p>The checkpoint was trained on games against the wheat baseline. It wins most valid games against that baseline and none against the two scripted agents. In one traced game, its first deviation from <code>Pipe7</code> occurred at decision 34, while both farms were still identical. States produced by a strong opponent were absent from the training data.</p>
    <h3>Action matching does not teach strategy</h3>
    <p>Rewarding the policy for selecting the expert's action is the imitation loss expressed as a reward. It cannot reward a different action that ends the game with more cash. Querying the script for its action after the learner has left the expert's trajectory is also invalid, because the script carries hidden state (its route, pending actions and selling mode) that no longer corresponds to the game. A script is deterministic only while its internal state and the game state agree.</p>

    <h2 id="future">Planned work: a hand-over curriculum for reinforcement learning</h2>
    <p>Applying PPO to the current policy would mainly optimise around these defects. The planned curriculum keeps the game state valid and exposes the learner to real outcomes.</p>
    <ol>
      <li>Select a seed, seat, opponent, script and hand-over day.</li>
      <li>The script plays from turn zero to the hand-over day.</li>
      <li>Control passes to the learner permanently.</li>
      <li>The game is played to the end, and the final cash is compared with a paired game in which the script played throughout.</li>
    </ol>
    <p>The hand-over day moves earlier in stages: the last three days, late investment, operation of an established farm, the opening, and finally all 719 decisions. Each stage must outperform its paired control before the next stage begins.</p>
""",
)

# =============================================================================== CUDA
CUDA = dict(
    hero=dict(img="citrus", accent="#c2410c", alt="Slices of orange, lemon, grapefruit and watermelon with ice cubes in rippling water."),
    title="A Verification-First Workflow for CUDA Kernel Optimization on Blackwell | Ritwika Kancharla",
    description="Contract CUDA work on the NVIDIA RTX PRO 6000 Blackwell: a kernel is accepted only if it is numerically correct, memory-safe and at least 1.2x faster than PyTorch on every workload.",
    eyebrow="Contract work, 2026",
    h1="A Verification-First Workflow for CUDA Kernel Optimization on Blackwell",
    meta=["Ritwika Kancharla", "2026", "Client work through Mercor"],
    links=[],
    abstract="""<p>This page describes the method I use for contract work writing CUDA kernels for the NVIDIA RTX PRO 6000 Blackwell (<code>sm_120</code>). Each task is a fixed deep-learning workload with a PyTorch reference implementation. A kernel is accepted only if it compiles for the target architecture, passes a numerical check on every output and gradient tensor, produces no Compute Sanitizer errors, and is at least 1.2&times; faster than the reference on every workload variant.</p>
<p>The client's source code is confidential, so the page covers the workflow and not the kernels. Two task tracks have been completed under these criteria. The current task is the backward pass of a cross-attention layer with 16 workload variants.</p>""",
    body="""
    <h2 id="problem">Problem statement</h2>
    <p>The acceptance criterion applies to every workload variant and not to their average. An optimisation that is faster on fifteen input shapes and slower on the sixteenth cannot be delivered. A kernel that is fast because it computes an incorrect gradient is a failed experiment and is recorded as one. This requirement determines the order of work: correctness is established on all shapes before any performance work begins, and every performance change is evaluated on the complete set.</p>

    <h2 id="method">Method</h2>
    <ol>
      <li>Measure the baseline on all shapes.</li>
      <li>If any output is incorrect, identify the first incorrect intermediate tensor.</li>
      <li>Profile the kernel and classify the bottleneck: compute, memory traffic, occupancy, launch overhead or synchronisation.</li>
      <li>Make one change and record the expected effect before measuring.</li>
      <li>Run the full workload set again. All 16 variants must pass.</li>
    </ol>
    <p>If a change causes a regression, the code is reverted and the note, the source snapshot and the measurements are kept. This record prevents the same idea from being attempted again without new evidence.</p>

    <h2 id="correctness">Establishing correctness</h2>
    <p>A backward pass can show many failing outputs that originate from one early error. The useful question is which intermediate tensor is the first to diverge. In the cross-attention task, the attention probabilities, context gradients, value gradients and output projections were all correct. The error began at the gradient of the attention scores and propagated from there into the query and key paths. This restricted the search to masking, scaling, memory layout, reductions and transposes around a single tensor.</p>
    <p>Compute Sanitizer then separates arithmetic errors from out-of-bounds accesses and data races. Correctness is tested on all shapes, because a launch geometry that is valid for the common sequence length of 77 can be invalid for another.</p>

    <h2 id="performance">Performance techniques</h2>
    <p>Once the profile identifies where time is spent, the following techniques were the most effective on Blackwell.</p>
    <ul>
      <li>Fusing adjacent pointwise operations into the preceding or following kernel.</li>
      <li>Tiling reductions so that reused values remain in registers or shared memory.</li>
      <li>A specialised path for the common sequence length, with a correct general path as the fallback.</li>
      <li>Fewer transfers to global memory for transposes and gradient accumulation.</li>
      <li>Calling the vendor GEMM where a hand-written matrix multiplication cannot compete.</li>
      <li>Batching small units of work so that launch cost is paid once.</li>
    </ul>
    <p>Speed is always measured end to end. A kernel that performs well in isolation can lose its advantage to a layout conversion or a temporary buffer after integration.</p>

    <h2 id="artifacts">Recorded artifacts</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Artifact</th><th>Purpose</th></tr></thead>
      <tbody>
        <tr><td>Iteration note</td><td>The change, the profile observation, the sanitizer result, and whether the change failed</td></tr>
        <tr><td>Source snapshot</td><td>The exact kernel behind each measurement, including rejected versions</td></tr>
        <tr><td>Benchmark JSON</td><td>Correctness and timing for every workload in machine-readable form</td></tr>
        <tr><td>Final report</td><td>Speedup per shape, numerical status and build details</td></tr>
      </tbody>
    </table></div>

    <h2 id="conclusions">Conclusions</h2>
    <ul>
      <li>Locate the first incorrect intermediate before any performance work.</li>
      <li>A profiler reading is a hypothesis about cause and should be tested by an experiment.</li>
      <li>Optimise the common shape without breaking the uncommon ones.</li>
      <li>Revert the code and keep the evidence.</li>
      <li>Spot checks give false confidence. Only the complete workload matrix is conclusive.</li>
    </ul>
""",
)

# =============================================================================== Routing
ROUTING = dict(
    hero=dict(img="lakeside", accent="#8f5f14", pos="50% 55%", alt="A stone lakeside path with flower urns at sunset, leading toward a village under steep hills."),
    title="Routing Foundation Models | Ritwika Kancharla",
    description="A 2025 research proposal with prototypes on learned warm starts for vehicle-routing solvers: a MILP-structured encoder, diffusion-based candidate generation, state-space decoding and feasibility repair.",
    eyebrow="Research proposal, 2025 to 2026",
    h1="Routing Foundation Models: Learned Warm Starts for Vehicle-Routing Solvers",
    meta=["Ritwika Kancharla", "2025 to 2026"],
    links=[("Monograph (PDF)", "../rfm_monograph.pdf"), ("Code", "https://github.com/ritwikareddykancharla/RoutingAGI")],
    abstract="""<p>Classical routing solvers enforce constraints reliably but are slow to run again on a large network that changes continuously. Neural routing policies are fast but tend to fail where operations cannot tolerate failure: they produce routes that violate a capacity or a time window, and they degrade when the instance distribution shifts. This work proposes a hybrid. A learned model supplies the solver with several diverse starting solutions, estimates near-term changes and makes fast local modifications, while the exact constraints and the solver remain responsible for feasibility.</p>
<p>The work consists of an 83-page monograph, two shorter manuscripts and prototype code. It is an architecture proposal with prototypes. It does not include a trained system that has been benchmarked against an industrial solver, and no such claim is made.</p>""",
    body="""
    <h2 id="problem">Problem statement</h2>
    <p>The interest in this problem comes from my time in Amazon's Supply Chain Optimization Technologies group, close to routing and middle-mile logistics. The variants of the vehicle-routing problem share most of their structure: depots, vehicles, demand, capacity, time, precedence and travel cost. Training a separate opaque network for each variant discards that shared structure. The goal is one family of components that represents an instance as a system of constraints, and that assists an exact solver without replacing it.</p>

    <h2 id="approach">Proposed components</h2>
    <h3>MILP-Transformer: a structure-aware encoder</h3>
    <p>The encoder takes the mixed-integer program itself as input: objective coefficients, variable bounds, constraint coefficients and the incidence between variables and constraints. Attention follows these relations and does not operate on a flattened text description of the instance.</p>
    <h3>Diffusion model for warm starts</h3>
    <p>A generative model samples many candidate assignments or tours. Diversity matters, because a solver benefits more from several distinct feasible starting points than from many variations of one greedy route. Denoising is biased toward valid capacity, timing and pickup-delivery pairing.</p>
    <h3>State-space decoding for long routes</h3>
    <p>A large instance decomposes into many vehicle tours, so the output sequence is long. State-space decoders (Mamba) scale linearly with sequence length and maintain a running state, which avoids quadratic attention at every output step.</p>
    <h3>Feasibility repair</h3>
    <p>A refinement step projects a nearly feasible solution onto the feasible set and can pass the result to a conventional solver.</p>

    <h2 id="variants">Problem variants covered</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Variant</th><th>Distinguishing constraint</th><th>Component studied</th></tr></thead>
      <tbody>
        <tr><td>CVRP</td><td>Vehicle capacity, return to depot</td><td>Diffusion warm starts with Mamba refinement</td></tr>
        <tr><td>VRPTW</td><td>Arrival time windows, waiting</td><td>Time-conditioned generation</td></tr>
        <tr><td>PDVRP</td><td>Pickup must precede its delivery</td><td>Paired tokens, precedence-aware repair</td></tr>
        <tr><td>MDVRP</td><td>Assignment of customers to depots</td><td>Depot-aware constraint graphs</td></tr>
        <tr><td>DVRP</td><td>Orders arrive during execution</td><td>Rollouts of a learned dynamics model, fast re-planning</td></tr>
      </tbody>
    </table></div>

    <h2 id="papers">Manuscripts and code</h2>
    <ul>
      <li><a href="../rfm_monograph.pdf"><em>Routing Foundation Model: A Unified Neural Optimization Framework for Large-Scale Routing and MILPs</em></a>. Monograph, 83 pages.</li>
      <li><a href="../milp_transformer.pdf"><em>MILP-Transformer: A Structure-Aware Neural Surrogate for Large-Scale Routing Optimization</em></a>. Manuscript.</li>
      <li><a href="../ssm-nco.pdf"><em>State-Space Autoregressive Decoding for Neural Combinatorial Optimization</em></a>. Position paper.</li>
      <li>Code: <a href="https://github.com/ritwikareddykancharla/diffusion-mamba-routing">diffusion-mamba-routing</a>, <a href="https://github.com/ritwikareddykancharla/constraint-graph-transformer">constraint-graph-transformer</a>, <a href="https://github.com/ritwikareddykancharla/routing-world-model">routing-world-model</a>, <a href="https://github.com/ritwikareddykancharla/proximal-refinement-networks">proximal-refinement-networks</a>.</li>
    </ul>
    <p>None of these manuscripts has been peer reviewed.</p>

    <h2 id="limitations">Limitations and required evaluation</h2>
    <p>The questions that determine whether the approach is useful remain open: the contribution of each component, the feasibility rate of the generated solutions, the optimality gap, the solver time that a warm start saves, transfer across instance sizes, and behaviour under network disruption.</p>
    <p>The appropriate next step is a comparison on public instance sets of three configurations on identical problems: the neural model alone, the solver alone, and the two combined. The comparison should report feasibility separately from solution quality, measure wall-clock time to a common optimality gap, and test transfer across instance sizes.</p>
""",
)
