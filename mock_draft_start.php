<?php
// mock_draft_start.php
session_start();

// Reset draft if requested
if (isset($_POST['reset_draft'])) {
    $_SESSION['my_team'] = [];
    $_SESSION['taken_players'] = [];
}

// Store settings if not already present
if (!isset($_SESSION['settings'])) {
    $_SESSION['settings'] = [
        'teams' => (int) $_POST['teams'],
        'format' => $_POST['format'],
        'scoring' => $_POST['scoring'],
        'roster' => [
            'qb' => (int) $_POST['qb'],
            'rb' => (int) $_POST['rb'],
            'wr' => (int) $_POST['wr'],
            'te' => (int) $_POST['te'],
            'flex' => (int) $_POST['flex'],
            'bench' => (int) $_POST['bench'],
        ]
    ];
}

if (!isset($_SESSION['my_team'])) {
    $_SESSION['my_team'] = [];
}

if (!isset($_SESSION['taken_players'])) {
    $_SESSION['taken_players'] = [];
}

if (isset($_POST['draft_player'])) {
    $picked = [
        'Player' => $_POST['player'],
        'position' => $_POST['position'],
        'fantasy_points' => $_POST['fantasy_points'],
        'grade' => $_POST['grade'],
        'label' => $_POST['label']
    ];
    $_SESSION['my_team'][] = $picked;
    $_SESSION['taken_players'][] = $_POST['player'];
}

if (isset($_POST['taken_by_other'])) {
    $_SESSION['taken_players'][] = $_POST['player'];
}

// Connect to DB
$mysqli = new mysqli("localhost", "root", "Richie30", "fantasy_football");

function fetch_players($mysqli, $table, $position) {
    $results = [];
    $query = "SELECT Player, PredictedFantasyPts_2025 AS fantasy_points, FinalGrade_2025 AS grade, GradeLabel_2025 AS label FROM $table ORDER BY FinalGrade_2025 DESC";
    $res = $mysqli->query($query);
    while ($row = $res->fetch_assoc()) {
        $row['position'] = strtoupper($position);
        $results[] = $row;
    }
    return $results;
}

$all_players = array_merge(
    fetch_players($mysqli, 'qb_2025_stats', 'qb'),
    fetch_players($mysqli, 'rb_2025_stats', 'rb'),
    fetch_players($mysqli, 'wr_2025_stats', 'wr'),
    fetch_players($mysqli, 'te_2025_stats', 'te')
);

usort($all_players, fn($a, $b) => $b['grade'] <=> $a['grade']);
$drafted_names = array_merge(array_column($_SESSION['my_team'], 'Player'), $_SESSION['taken_players']);
$filtered_players = array_filter($all_players, fn($p) => !in_array($p['Player'], $drafted_names));

$filter = $_GET['filter'] ?? 'all';
if ($filter !== 'all') {
    $filtered_players = array_filter($filtered_players, fn($p) => strtolower($p['position']) === strtolower($filter));
}

function count_position($team, $pos) {
    return count(array_filter($team, fn($p) => strtolower($p['position']) === strtolower($pos)));
}

function suggest_pick($available, $team, $settings) {
    $counts = [
        'qb' => count_position($team, 'QB'),
        'rb' => count_position($team, 'RB'),
        'wr' => count_position($team, 'WR'),
        'te' => count_position($team, 'TE'),
    ];

    $best = null;
    $best_grade = -1;

    foreach ($available as $p) {
        $pos = strtolower($p['position']);
        $total_needed = ($pos === 'rb' || $pos === 'wr') ? $settings[$pos] + $settings['flex'] : ($settings[$pos] ?? 0);

        if (($counts[$pos] ?? 0) < $total_needed && $p['grade'] > $best_grade) {
            $best = $p;
            $best_grade = $p['grade'];
        }
    }

    return $best ?? ($available[array_key_first($available)] ?? null);
}

$suggestion = suggest_pick($filtered_players, $_SESSION['my_team'], $_SESSION['settings']['roster']);
?>

<!DOCTYPE html>
<html>
<head>
    <title>Mock Draft Board</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="bg-light">
<div class="container mt-5">
    <h2 class="mb-4">📋 Mock Draft: Best Available Players</h2>

    <div class="mb-3 d-flex justify-content-between align-items-center">
        <form method="get" class="d-flex gap-2">
            <label class="form-label me-2">Filter by Position:</label>
            <select name="filter" class="form-select" onchange="this.form.submit()">
                <option value="all" <?= $filter === 'all' ? 'selected' : '' ?>>All</option>
                <option value="qb" <?= $filter === 'qb' ? 'selected' : '' ?>>QB</option>
                <option value="rb" <?= $filter === 'rb' ? 'selected' : '' ?>>RB</option>
                <option value="wr" <?= $filter === 'wr' ? 'selected' : '' ?>>WR</option>
                <option value="te" <?= $filter === 'te' ? 'selected' : '' ?>>TE</option>
            </select>
        </form>

        <?php if ($suggestion): ?>
            <div class="alert alert-primary mb-0">
                🤖 Recommended Pick: <strong><?= $suggestion['position'] ?> - <?= $suggestion['Player'] ?></strong>
                (<?= number_format($suggestion['grade'], 1) ?> Grade, <?= $suggestion['label'] ?>)
            </div>
        <?php endif; ?>
    </div>

    <div class="row">
        <div class="col-md-8">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Position</th>
                        <th>Projected Points</th>
                        <th>Grade</th>
                        <th>Tier</th>
                        <th colspan="2"></th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($filtered_players as $player): ?>
                        <tr>
                            <td><?= htmlspecialchars($player['Player']) ?></td>
                            <td><?= $player['position'] ?></td>
                            <td><?= number_format($player['fantasy_points'], 1) ?></td>
                            <td><?= number_format($player['grade'], 1) ?></td>
                            <td><?= $player['label'] ?></td>
                            <td>
                                <form method="post" style="margin:0">
                                    <input type="hidden" name="draft_player" value="1">
                                    <input type="hidden" name="player" value="<?= htmlspecialchars($player['Player']) ?>">
                                    <input type="hidden" name="position" value="<?= $player['position'] ?>">
                                    <input type="hidden" name="fantasy_points" value="<?= $player['fantasy_points'] ?>">
                                    <input type="hidden" name="grade" value="<?= $player['grade'] ?>">
                                    <input type="hidden" name="label" value="<?= $player['label'] ?>">
                                    <button type="submit" class="btn btn-sm btn-success">Draft</button>
                                </form>
                            </td>
                            <td>
                                <form method="post" style="margin:0">
                                    <input type="hidden" name="taken_by_other" value="1">
                                    <input type="hidden" name="player" value="<?= htmlspecialchars($player['Player']) ?>">
                                    <button type="submit" class="btn btn-sm btn-outline-danger">Taken by Other</button>
                                </form>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>

        <div class="col-md-4">
            <div class="bg-white p-3 rounded shadow-sm">
                <h5 class="mb-3">🧑‍💻 Your Team</h5>
                <ul class="list-group">
                    <?php foreach ($_SESSION['my_team'] as $p): ?>
                        <li class="list-group-item d-flex justify-content-between">
                            <span><?= $p['position'] ?> - <?= $p['Player'] ?></span>
                            <small><?= $p['label'] ?> (<?= $p['grade'] ?>)</small>
                        </li>
                    <?php endforeach; ?>
                </ul>
                <form method="post" class="mt-3">
                    <input type="hidden" name="reset_draft" value="1">
                    <button type="submit" class="btn btn-danger w-100">Reset Draft</button>
                </form>
            </div>
        </div>
    </div>

    <div class="mt-4 text-end">
        <a href="mock_draft.php" class="btn btn-secondary">← Back</a>
    </div>
</div>
</body>
</html>
