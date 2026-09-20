"""The two ARC Prize 2026 project pages. Figures come from tools/build_arc3_figures.py and build_arc2_figures.py."""

I3 = "../assets/img/arc3/"
I2 = "../assets/img/arc2/"


def grid(src, w, h, alt, label, small=False):
    cls = "g small" if small else "g"
    return f'<div class="{cls}"><img src="{I2}{src}.png" width="{w}" height="{h}" alt="{alt}"><span>{label}</span></div>'


TO = '<div class="to" aria-hidden="true">&rarr;</div>'

# =============================================================================== ARC-AGI-3
ARC3 = dict(
    title="Verified World Models for ARC-AGI-3 | Ritwika Kancharla",
    description="An open 27B language model paired with a deterministic verification harness completes two public ARC-AGI-3 games (14 of 14 levels) without fine-tuning.",
    eyebrow="ARC Prize 2026, ongoing",
    h1="Verified World Models for Interactive Reasoning in ARC-AGI-3",
    meta=["Ritwika Kancharla", "September 2026", "Work in progress"],
    links=[("Competition", "https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3"),
           ("Development PR", "https://github.com/ritwikareddykancharla/arc-agi3/pull/6")],
    abstract="""<p>ARC-AGI-3 evaluates an agent on small interactive games for which no rules, goals or instructions are provided. This project studies whether an open-weight 27B language model (Qwen3.8-27B), used without any fine-tuning, can solve such games when it is paired with a deterministic software harness. The model is responsible only for proposing hypotheses about the game. The harness is responsible for perception, for recording every state transition, for testing each proposed rule against the recorded history, and for executing plans under explicit guard conditions.</p>
<p>With this division of responsibility the system completed all 6 levels of the public game <code>ft09</code> and all 8 levels of the public game <code>sb26</code>. Both games were used during development. The results therefore validate the design of the harness and should not be read as an estimate of leaderboard performance.</p>""",
    body=f"""
    <figure class="fig"><div class="plate"><div class="frames">
      <div><div class="frame"><img src="{I3}ft09-play.gif" width="256" height="270" alt="Animation of the game ft09 played from the first level to the last. Tiles in a grid change colour one click at a time until each level completes."></div><span class="cap">ft09: 6 of 6 levels, 75 actions</span></div>
      <div><div class="frame"><img src="{I3}sb26-play.gif" width="256" height="270" alt="Animation of the game sb26. Coloured tokens are selected from a row at the bottom and placed into slots inside framed containers, level after level."></div><span class="cap">sb26: 8 of 8 levels, 124 actions</span></div>
    </div></div>
    <figcaption><b>Figure 1.</b> Qwen3.8-27B playing the two public games. Every frame is taken from the saved run logs. The row of squares beneath each game counts completed levels. The model received no description of the games, the actions or the objective.</figcaption></figure>

    <h2 id="problem">Problem statement</h2>
    <p>In ARC-AGI-2 a solver receives several solved examples and one test input. ARC-AGI-3 removes the examples. The agent receives a 64&times;64 frame with 16 colours and a small action set: four directional actions, a few buttons, and a click at a chosen coordinate. It must determine, by acting, which parts of the frame belong to the game world, what each action does, and what condition completes a level. The score rewards action efficiency, measured as the number of real actions the agent needs.</p>
    <p>Levels within one game share their mechanics and increase in difficulty. Figure 2 shows the opening frame of every level of the two games studied here.</p>

    <figure class="fig wide"><div class="plate">
      <div class="frame"><img src="{I3}ft09-levels.png" width="1192" height="192" alt="Six opening frames of ft09, one per level. Each shows a grid of square tiles in two colours with a few small patterned tiles."></div>
      <span class="cap" style="margin-bottom:18px">ft09, levels 1 to 6</span>
      <div class="frame"><img src="{I3}sb26-levels.png" width="1592" height="192" alt="Eight opening frames of sb26, one per level. Each has a row of coloured outlines at the top, framed boxes with empty slots in the middle, and a row of coloured tokens at the bottom."></div>
      <span class="cap">sb26, levels 1 to 8</span>
    </div>
    <figcaption><b>Figure 2.</b> Opening frames. In <code>ft09</code> a few tiles carry a small pattern that specifies the target state of a panel. In <code>sb26</code> a target row at the top specifies the order in which tokens must be read from the boxes below; from level 2 onward, boxes refer to other boxes.</figcaption></figure>

    <p>The research question is one of transfer. Recent work on executable world models for this benchmark (WorldCoder, Schema, Retrodict, Tycho) relies on frontier models behind an API. This project asks how much of that approach remains effective when the model is a 27B open-weight model that can be served on a single GPU.</p>

    <h2 id="baseline">Baseline and its failure modes</h2>
    <p>The baseline agent presents the current frame to the model, lets it reason, executes the action it names, and repeats. This agent fails in the same three ways on almost every game.</p>
    <ol>
      <li><strong>Perception.</strong> Given a 64&times;64 grid as text, the model spends thousands of tokens transcribing rows and still misplaces object boundaries.</li>
      <li><strong>Untested hypotheses.</strong> The model holds several explanations of an action at once (select, toggle, move) and does not design an action that would distinguish them.</li>
      <li><strong>Loss of established facts.</strong> Once the context fills, a fact established on level 1 is derived again, sometimes incorrectly, on level 4.</li>
    </ol>
    <p>A larger reasoning budget does not remove any of these failures. Additional reasoning is useful only after the model is given a correct structured description of the game.</p>

    <h2 id="approach">Approach</h2>
    <p>The system separates proposing from checking. The language model proposes what the objects are, what an action does, and what completes a level. A deterministic Python harness, which contains no learned components, owns every operation that can be computed or verified exactly.</p>
    <div class="tablewrap"><table>
      <thead><tr><th>Component</th><th>Function</th></tr></thead>
      <tbody>
        <tr><td>Perception</td><td>Extracts connected regions, boxes, repeated shapes and tile grids with coordinates, and presents them as a table. It assigns no meaning to any object.</td></tr>
        <tr><td>Transition ledger</td><td>Stores the frame before, the action, the frame after and the exact set of changed cells for every real action. When a model note contradicts the ledger, the harness cites the contradicting transition.</td></tr>
        <tr><td>Rule verification</td><td>Replays each proposed rule over the full recorded history and reports the first transition at which it fails.</td></tr>
        <tr><td>Guarded execution</td><td>A multi-action plan carries the cell changes the model expects. The harness executes one action at a time and halts at the first deviation.</td></tr>
        <tr><td>Turn scheduling</td><td>Separates discovery turns from execution turns. A fully verified plan is executed without asking the model to reason about it again.</td></tr>
      </tbody>
    </table></div>
    <p>The first actions on a new game are probes: single actions chosen to answer one question. Figure 3 shows the first action of the <code>sb26</code> run.</p>

    <figure class="fig text"><div class="plate"><div class="frame"><img src="{I3}sb26-probe-1.png" width="656" height="320" alt="Two frames side by side. On the left a circle marks a token in the bottom row being clicked. On the right the same token has a white ring around it."></div></div>
    <figcaption><b>Figure 3.</b> A probe action, before and after. The circle marks the click; the box on the right marks the 20 cells that changed. The model's stated purpose was: &ldquo;click bottom solid piece to learn interaction model (select vs move). Expect it to be removed from source if it moves.&rdquo; The token was not removed and gained a ring, which establishes that a click selects.</figcaption></figure>

    <h2 id="cases">Case studies</h2>
    <h3>ft09: a relation between distant regions</h3>
    <p>Without assistance the model treated each panel of tiles as a separate puzzle. The missing element was a relation between regions that are far apart on screen: the small patterned tile inside a panel is a miniature of that panel's target state. Clicking a tile toggles its colour, and the level completes when every panel matches its miniature.</p>
    <p>The harness was not changed to state this rule. It was changed to report panels in pairs, to express tile coordinates in panel space rather than pixel space, and to list reflections and colour permutations between regions as candidate relations. After this change the model's plans took the following form.</p>
    <blockquote><p>Toggle BR tile (36,52) from blue to red to match micro swatch 0 at row2,col0. This is the last mismatch; expect level completion.</p><cite>Qwen3.8-27B, third action of the completed ft09 run</cite></blockquote>
    <p>The run completed all six levels in 75 actions and 26 model calls, in about eleven minutes. No action produced a result that the model had not predicted.</p>

    <h3>sb26: references between containers</h3>
    <p>The top row gives the order in which tokens must appear. The boxes in the middle contain slots. From level 2 onward, some slots contain a hollow token in the colour of another box, which means that reading continues inside that box. A depth-first reading of the boxes yields one sequence, and the level completes when that sequence equals the top row.</p>
    <p>A flat list of connected regions cannot express this structure. The harness therefore constructs a small graph: boxes contain slots, slots contain solid tokens or hollow references, and a hollow reference may point to the box of the same colour. The graph is built in 12 to 15 ms per frame and carries no interpretation of its edges. Given the graph, the model proposed the depth-first reading, the harness verified it against every completed level, and the remaining levels were solved largely by bookkeeping.</p>
    <p>The run shown in Figure 1 used 124 actions and 90 model calls over 44 minutes. Thirteen actions produced an outcome the model had not predicted. In each case the harness halted the plan and the model revised its description.</p>

    <h2 id="results">Results</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Game</th><th class="r">Levels</th><th class="r">Actions</th><th class="r">Model calls</th><th class="r">Mispredicted</th><th>Run conditions</th></tr></thead>
      <tbody>
        <tr><td><code>ft09</code></td><td class="r">6 / 6</td><td class="r">75</td><td class="r">26</td><td class="r">0</td><td>Single run from empty memory</td></tr>
        <tr><td><code>sb26</code></td><td class="r">8 / 8</td><td class="r">124</td><td class="r">90</td><td class="r">13</td><td>Completed across several resumed sessions</td></tr>
      </tbody>
    </table></div>

    <h2 id="negative">Negative results</h2>
    <h3>An all-or-nothing verifier provides no gradient</h3>
    <p>The first verifier asked the model for a complete simulator and counted a transition as correct only if all 4,096 cells matched. One wrong cell scored the same as a crash, and because the simulated state was rolled forward, one early error invalidated every later transition. The verifier now reports separately whether the code ran, how many transitions are exact, what fraction of cells is correct, and which transition fails first. New code replaces old code only if it improves on this backtest.</p>
    <h3>Persistent memory can preserve an incorrect belief</h3>
    <p>In one resumed <code>sb26</code> session the model's notes still stated that a click erases and repaints a token, long after the ledger showed the token moving as a block. Notes are now presented together with their age and with the harness's own record of what each action caused.</p>
    <h3>Context compaction removed the most relevant evidence</h3>
    <p>Naive summarisation kept long early discussions of pixels and discarded recent evidence. The current level is now kept in full, completed levels are removed oldest first, and what was learned from them is kept as a short rule with its counterexamples.</p>
    <h3>Repeated verification of verified plans</h3>
    <p>Even when exact target cells had been computed, the model spent thousands of tokens checking coordinates again. Separating discovery turns from execution turns removed most of this cost on later levels.</p>

    <h2 id="limitations">Limitations</h2>
    <p>Both games were inspected during development, so they constitute a development set. The <code>sb26</code> result was obtained across resumed sessions and is not a single uninterrupted run. No result here is a Kaggle score, and there is currently no evidence about games that were not studied during development.</p>

    <h2 id="future">Future work</h2>
    <ul>
      <li>Freeze the harness and repeat both games from empty memory several times to measure how reliably they are completed.</li>
      <li>Extend to the remaining public games, adding one general representation for the earliest failure observed on each.</li>
      <li>Report time, tokens, real actions and the number of harness interventions as separate quantities.</li>
      <li>Package the model and harness for the offline Kaggle GPU environment and measure how many games can run concurrently within the available KV cache.</li>
      <li>Train on intermediate decisions (object roles, discriminating probes, repair location, stopping) and not only on final action sequences.</li>
    </ul>
""",
)

# =============================================================================== ARC-AGI-2
ARC2 = dict(
    title="Verified Program Induction for ARC-AGI-2 | Ritwika Kancharla",
    description="A second ARC-AGI-2 solver in which a 27B model writes each puzzle's rule as a program that must reproduce the training pairs exactly. Verified programs are correct on the test grid in 10 of 15 cases.",
    eyebrow="ARC Prize 2026, ongoing",
    h1="Verified Program Induction for ARC-AGI-2",
    meta=["Ritwika Kancharla", "September 2026", "Work in progress"],
    links=[("Competition", "https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-2")],
    abstract="""<p>My current ARC-AGI-2 submission scores 33.89 on the public leaderboard. It is a transductive solver: a fine-tuned Qwen3-4B generates the answer grid one cell at a time, and the answer is never checked against the training examples. This project adds a second, inductive solver. Qwen3.8-27B writes the transformation rule as a Python function, a harness executes the function on the training inputs, and the model receives the exact mismatching cells until the function reproduces every training pair.</p>
<p>Most improvements came from analysing the model's reasoning traces, identifying information it could not extract reliably from a grid, and supplying that information as a computed fact. The main finding is negative. A program that reproduces every training pair and passes every additional check is correct on the test grid in only 10 of 15 cases (67%), and agreement between independently sampled programs does not raise that rate. The central problem is therefore candidate selection, not program synthesis. The two solvers have not yet been merged into a submission.</p>""",
    body=f"""
    <h2 id="problem">Problem statement</h2>
    <p>Each ARC task provides a small number of input and output grids that share one hidden transformation, followed by one or more test inputs. Every task uses a different transformation, so the rule must be inferred from the examples alone. A solver may submit two attempts per test grid, and an attempt is correct only if every cell matches. The public evaluation set contains 120 tasks. The competition runs offline on four L4 GPUs with a 12-hour limit.</p>

    <figure class="fig wide"><div class="plate"><div class="grids n4">
      {grid("13e47133-train1-in", 261, 261, "A mostly yellow 20 by 20 grid divided into regions by red lines, with a few single coloured pixels in the corner of each region.", "training input")}{TO}
      {grid("13e47133-train1-out", 261, 261, "The same grid with every region filled by nested rectangular rings in the colours of its corner pixels.", "training output")}
      {grid("13e47133-test0-in", 241, 241, "A larger 30 by 30 green grid with pale blue dividing lines and corner pixels. Some regions are not rectangles.", "<b>test input</b>, 30&times;30")}{TO}
      {grid("13e47133-test0-out", 241, 241, "The expected answer. Each region of the test grid is filled with nested rings that follow its edge, including the L-shaped regions.", "expected output")}
    </div></div>
    <figcaption><b>Figure 1.</b> Task <code>13e47133</code>. Lines divide the grid into regions. Seed pixels in the corner of a region define a colour sequence, and the region is filled with rings of those colours from its edge inward. The test grid is larger than any training grid and contains non-rectangular regions. The inductive solver solved this task after two repair rounds.</figcaption></figure>

    <h2 id="baseline">Baseline</h2>
    <p>The baseline is the public NVARC notebook, which scores 33.89. For each task it fine-tunes a Qwen3-4B model on that task's own training pairs, augmented by rotation, reflection and colour permutation into 128 copies. It then decodes candidate answers from 16 views of the test grid and submits the two with the highest model likelihood.</p>
    <p>The baseline has one structural weakness. The answer in Figure 1 contains 900 cells. The model must emit 900 correct tokens in sequence, a single error scores zero, and the answer is never compared with the training examples. A program of about 25 lines that encodes the correct rule produces all 900 cells at once. Its correctness on the training pairs can also be established before the test grid is considered, because the training pairs serve as unit tests.</p>

    <h2 id="approach">Approach</h2>
    <ol>
      <li><strong>Fact sheet.</strong> The harness computes task-level facts: objects and bounding boxes, changed cells, colour transitions, and size relations that hold in every training pair.</li>
      <li><strong>Inspection turn.</strong> The model's first turn must be code that inspects the grids. It runs numpy on the actual data with helper functions such as <code>objects()</code> and <code>panels()</code> available. Extended reasoning is enabled only after this turn.</li>
      <li><strong>Synthesis.</strong> The model writes <code>transform(grid)</code>. The harness executes it in a sandbox on every training input.</li>
      <li><strong>Repair.</strong> If any cell is wrong, the model receives the exact mismatch, for example &ldquo;row 2: predicted 0000000, expected 1110000&rdquo;, and revises the function. Up to three repair rounds are allowed.</li>
      <li><strong>Selection.</strong> Programs that reproduce every training pair pass through additional checks and a vote, which produce the two submitted answers.</li>
    </ol>
    <p>This is the static counterpart of the approach used for <a href="arc-agi-3.html">ARC-AGI-3</a>. The training pairs play the role of the recorded history, the program is the model's hypothesis, and testing the hypothesis against the history has negligible cost.</p>

    <h2 id="traces">Analysis of reasoning traces</h2>
    <p>The harness streams the model's reasoning for every attempt to disk. Each change to the harness listed below was motivated by a specific observation in these traces.</p>
    <div class="tablewrap"><table>
      <thead><tr><th>Observation</th><th>Change to the harness</th></tr></thead>
      <tbody>
        <tr><td>The model reasoned for 16,000 tokens, reached the limit and returned no program. A single cell lookup cost about 2,000 tokens.</td><td>When a reply is truncated, the model's own notes are returned to it with a request for a program. An approximate program can be verified and repaired; a truncated reply cannot.</td></tr>
        <tr><td>Rows were transcribed digit by digit and miscounted.</td><td>Grids are displayed with row and column indices, and the model can execute code on them.</td></tr>
        <tr><td>Output dimensions were derived by hand on every attempt.</td><td>The fact sheet states size rules directly, for example &ldquo;in every pair the output is the bounding box of colour 8&rdquo;.</td></tr>
        <tr><td>About 5,000 tokens were spent before the first inspection of the data.</td><td>The first turn runs with extended reasoning disabled and must inspect the data.</td></tr>
        <tr><td>The model wrote <code>if h == 5 and w == 13: out[2, 8] = 1</code>, which memorises a training pair by its size.</td><td>The verifier rejects programs that branch on exact training dimensions, and programs that leave the test grid unchanged when every training pair changes.</td></tr>
        <tr><td>Asked to repair an out-of-bounds error, the model wrote <code>out[i, j] = background</code>.</td><td>The repair prompt states that a constant fallback is rarely the rule and asks for a second derivation of those cells.</td></tr>
      </tbody>
    </table></div>

    <h2 id="cases">Case studies</h2>
    <h3>Off-centre symmetry (task 0934a4d8)</h3>
    <p>The input is a symmetric pattern with a rectangular region masked out. The required output is the content of the masked region. The first three versions of the harness obtained no program at all, because the model exhausted its budget reading digits. Figure 2 shows the effect of adding computed symmetry facts.</p>
    <figure class="fig"><div class="plate"><div class="grids n3">
      {grid("0934a4d8-test0-in", 331, 331, "A dense, colourful 30 by 30 symmetric pattern with a sky blue rectangle covering nine rows and three columns at the left edge.", "test input; the masked region is at the left edge")}
      {grid("0934a4d8-v7", 57, 153, "A 9 by 3 answer grid in which twelve cells are outlined in red as wrong.", '<b class="bad">12 cells wrong</b><br>assumed a centred mirror axis', True)}
      {grid("0934a4d8-v9", 57, 153, "The same answer grid with only two cells outlined in red.", '<b class="bad">2 cells wrong</b><br>fact sheet lists all three mirror partners', True)}
      {grid("0934a4d8-v11", 49, 145, "The answer grid with no cells outlined.", '<b class="ok">correct</b><br>fact sheet adds a weak diagonal symmetry', True)}
    </div></div>
    <figcaption><b>Figure 2.</b> One task and one model under three versions of the fact sheet. Red outlines mark wrong cells. The model repeatedly assumed reflection about the centre of the grid (<code>x</code> to <code>29 - x</code>). The true axis is offset by one cell (<code>31 - x</code>). Once the fact sheet stated the offset explicitly, the model found the rule on its first attempt.</figcaption></figure>
    <p>The last two cells have no usable mirror partner: the horizontal partner lies outside the grid and the vertical partner lies inside the masked region. The grid is also approximately symmetric about the diagonal, with 49% agreement, which is well above chance but far from exact. This was added to the fact sheet and labelled as a weak cue. One of three programs used it as a last resort and was correct. It lost the vote two to one and was submitted only because two attempts are allowed.</p>

    <h3>Ambiguous anchoring (task 221dfab4)</h3>
    <p>The task recolours every sixth row. Three of four programs wrote <code>if y % 6 == 0</code>, which counts rows from the top. Both training grids have 29 rows, and at that height counting from the top and counting from the marker at the bottom select the same rows. The test grids have 25 and 30 rows. The training pairs cannot distinguish the two hypotheses.</p>
    <figure class="fig wide"><div class="plate"><div class="grids n4">
      {grid("221dfab4-train0-in", 221, 291, "A 29 by 22 training input: pale blue shapes on a blue background with a short yellow marker at one edge.", "training input, 29 rows")}{TO}
      {grid("221dfab4-train0-out", 221, 291, "The training output: a column of alternating yellow and green stripes, with every sixth row of the shapes recoloured green.", "training output")}
      {grid("221dfab4-wrong", 309, 309, "A 25 by 25 answer in which many cells are outlined in red because the green stripes are on the wrong rows.", '<b class="bad">118 cells wrong</b><br>rows counted from the top')}
      {grid("221dfab4-right", 301, 301, "The same 25 by 25 answer with the green stripes on the correct rows.", '<b class="ok">correct</b><br>rows counted from the marker')}
    </div></div>
    <figcaption><b>Figure 3.</b> Both programs reproduce both training pairs exactly. Only one remains correct when the grid height changes. In 84 of the 120 public evaluation tasks the test grid has a size that does not occur among the training grids.</figcaption></figure>
    <p>The correct program lost the vote three to one. It was selected by a robustness criterion: each program is executed on reflected and rotated copies of the training pairs, and programs that remain correct are preferred. A program that follows the marker is invariant to reflection, and one that counts from row 0 is not. The correct program scored 1.00 on this criterion and the others scored 0.43.</p>

    <h3>Structure in the added cells (task 142ca369)</h3>
    <p>The model traced diagonals cell by cell for about 40,000 tokens without identifying the structure of the added cells, because a list of changed cells carries no shape information. The harness now groups added cells into straight segments and reports each segment with its endpoints and the objects it touches.</p>
    <figure class="fig wide"><div class="plate"><div class="grids n3">
      {grid("142ca369-in", 321, 321, "A black 20 by 20 grid with four small L-shaped objects along a diagonal and four single pixels in a column, one pair per colour.", "input")}{TO}
      {grid("142ca369-out", 321, 321, "The output. From each L-shape a diagonal line runs down to the single pixel of the same colour and then up to the right edge.", "output")}
      {grid("142ca369-segments", 321, 321, "The output with a thin line drawn over each straight run of added cells, showing two segments per colour that meet at the single pixel.", "segments reported by the harness: <b>two per colour, meeting at the single pixel</b>")}
    </div></div>
    <figcaption><b>Figure 4.</b> Segment extraction. With segments on the fact sheet, the model described the structure correctly within about 4,000 tokens. It has not yet produced a fully correct program for this task; one of the two test grids is solved.</figcaption></figure>

    <h3>Exact on the training pairs, incorrect on the test grid (task 28a6681f)</h3>
    <p>The blue cells in this task behave like a liquid. They leave their original position and fill the enclosed cavities level by level from the bottom.</p>
    <figure class="fig wide"><div class="plate"><div class="grids n4">
      {grid("28a6681f-train0-in", 221, 221, "A 10 by 10 training input with green and red walls and a double column of blue cells at the right edge.", "training input")}{TO}
      {grid("28a6681f-train0-out", 221, 221, "The training output. The blue cells have left the right column and filled the gap between two walls.", "training output")}
      {grid("28a6681f-pred", 229, 229, "The model's answer for the test grid with four cells outlined in red.", '<b class="bad">4 cells wrong</b><br>program output')}
      {grid("28a6681f-test0-out", 221, 221, "The correct answer. The blue cells fill the lowest gaps first, including the wide gap at the lower left.", "expected output")}
    </div></div>
    <figcaption><b>Figure 5.</b> Three programs reproduced all three training pairs exactly, and all three were wrong on the test grid. Each fills a single column. In every training pair only one cavity is open at each height, so filling one column and filling by level are indistinguishable. The test grid has two cavities at the same height.</figcaption></figure>

    <h2 id="results">Results</h2>
    <p>Every program produced in the saved runs (11 tasks, 18 test grids) was executed again under the current verification checks.</p>
    <div class="tablewrap"><table>
      <thead><tr><th>Quantity</th><th class="r">Value</th></tr></thead>
      <tbody>
        <tr><td>Test grids for which at least one program passed every check</td><td class="r">15 of 18</td></tr>
        <tr class="best"><td>Of those, grids on which the selected answer was correct</td><td class="r">10 of 15 (67%)</td></tr>
        <tr><td>The same, restricted to grids where two or more programs agreed</td><td class="r">3 of 5 (60%)</td></tr>
      </tbody>
    </table></div>
    <p>Two conclusions follow. First, reproducing every training pair and passing every current check gives a correct answer about two times in three. Second, agreement between samples of the same model is not independent evidence, because the samples share the same misconceptions, as task <code>28a6681f</code> shows. The sample is small and these estimates will change.</p>
    <p>On the most recent 20-task run, which was stopped early, six tasks had finished. Four were solved, one had one of two test grids correct, and <code>28a6681f</code> was incorrect. Harder tasks, such as <code>142ca369</code> and <code>16b78196</code>, do not reach a program that reproduces the training pairs within three repair rounds.</p>

    <h2 id="merge">Combining the two solvers</h2>
    <p>The intended system submits the verified program's answer as one attempt and keeps a baseline answer as the other. An early version of my notes stated that this combination can only add solved tasks. That statement is incorrect. The baseline already produces two answers, so giving one attempt to a program's answer removes a baseline answer. If the removed answer was correct and the program belongs to the incorrect third, a solved grid becomes unsolved.</p>
    <p>The merge is therefore treated as a selection of two answers from up to four candidates. By default it never displaces the baseline's first answer, and it reports the number of grids gained and the number lost. The best policy is an empirical question that requires running both solvers on the same complete task set.</p>

    <h2 id="limitations">Limitations and future work</h2>
    <ul>
      <li>There is no merged submission, so 33.89 remains the only leaderboard result.</li>
      <li>All experiments use a hosted or self-served 27B model that produces up to 19,000 reasoning tokens per reply. This does not fit the offline budget of four L4 GPUs for 12 hours, which is shared with the baseline.</li>
      <li>The saved traces (every reply, program and verification report) are intended as training data for a smaller local model. That work has not started.</li>
      <li>The selection problem remains open. Executing a program establishes that it fits the training pairs. It does not establish that the program is still correct when the grid changes.</li>
    </ul>
""",
)
