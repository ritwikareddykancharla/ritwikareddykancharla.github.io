"""The two ARC Prize 2026 project pages. Figures come from tools/build_arc3_figures.py and build_arc2_figures.py."""

I2 = "../assets/img/arc2/"


def grid(src, w, h, alt, label, small=False):
    cls = "g small" if small else "g"
    return f'<div class="{cls}"><img src="{I2}{src}.png" width="{w}" height="{h}" alt="{alt}"><span>{label}</span></div>'


TO = '<div class="to" aria-hidden="true">&rarr;</div>'

# =============================================================================== ARC-AGI-2
ARC2 = dict(
    hero=dict(img="hooded-cats", accent="#c2372e", alt="Painted cats wearing hoods in different floral patterns, scattered with blue stars on a cream background."),
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
