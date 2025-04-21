<?php
$playerName = isset($_GET['player']) ? urldecode($_GET['player']) : '';
$position = isset($_GET['position']) ? strtolower($_GET['position']) : 'qb';

if (empty($playerName) || !in_array($position, ['qb', 'rb', 'wr', 'te'])) {
    echo "❌ Invalid or missing player or position.";
    exit;
}

$conn = new mysqli("localhost", "root", "Richie30", "fantasy_football");
if ($conn->connect_error) {
    die("❌ Connection failed: " . $conn->connect_error);
}

$yearlyStats = [];
for ($year = 2020; $year <= 2024; $year++) {
    $table = "{$position}_{$year}_stats";
    $check = $conn->query("SHOW TABLES LIKE '$table'");

    if ($check && $check->num_rows > 0) {
        $query = $conn->prepare("SELECT * FROM $table WHERE Player = ?");
        $query->bind_param("s", $playerName);
        $query->execute();
        $result = $query->get_result();

        if ($row = $result->fetch_assoc()) {
            $row = array_change_key_case($row, CASE_LOWER);
            $row['year'] = $year;
            $yearlyStats[] = $row;
        }

        $query->close();
    }
}

// Fetch 2025 prediction
$predictionTable = "{$position}_2025_stats";
$tableCheck = $conn->query("SHOW TABLES LIKE '$predictionTable'");
$predictions = null;

if ($tableCheck && $tableCheck->num_rows > 0) {
    $predFetch = $conn->prepare("SELECT * FROM $predictionTable WHERE Player = ?");
    $predFetch->bind_param("s", $playerName);
    $predFetch->execute();
    $predResult = $predFetch->get_result();
    $predictions = $predResult->fetch_assoc();
    $predFetch->close();
}
?>

<!DOCTYPE html>
<html>
<head>
    <title><?= htmlspecialchars($playerName) ?> - Player Page</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<?php include __DIR__ . '/nav_bar.php'; ?>

<div class="container mt-5">
    <h2 class="mb-4"><?= htmlspecialchars($playerName) ?> - <?= strtoupper($position) ?> Player Page</h2>

    <div class="card mb-4">
        <div class="card-header bg-dark text-white">📊 Year-by-Year Stats (2020–2024)</div>
        <div class="card-body p-0">
            <table class="table table-striped table-hover m-0">
                <thead>
                    <tr>
                        <th>Year</th>
                        <?php if ($position === 'qb'): ?>
                            <th>Pass Yards</th>
                            <th>Pass TDs</th>
                            <th>INTs</th>
                        <?php endif; ?>
                        <th>Rush Yards</th>
                        <th>Rush TDs</th>
                        <?php if ($position !== 'qb'): ?>
                            <th>Rec Yards</th>
                            <th>Rec TDs</th>
                            <th>Receptions</th>
                        <?php endif; ?>
                        <th>Fantasy Points</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($yearlyStats)): ?>
                        <tr><td colspan="10" class="text-center">No data found from 2020–2024.</td></tr>
                    <?php else: ?>
                        <?php foreach ($yearlyStats as $stat): ?>
                            <tr>
                                <td><?= $stat['year'] ?></td>
                                <?php if ($position === 'qb'): ?>
                                    <td><?= $stat['pass_yards'] ?? '' ?></td>
                                    <td><?= $stat['pass_tds'] ?? '' ?></td>
                                    <td><?= $stat['interceptions'] ?? '' ?></td>
                                <?php endif; ?>
                                <td><?= $stat['rush_yards'] ?? '' ?></td>
                                <td><?= $stat['rush_tds'] ?? '' ?></td>
                                <?php if ($position !== 'qb'): ?>
                                    <td><?= $stat['rec_yards'] ?? '' ?></td>
                                    <td><?= $stat['rec_tds'] ?? '' ?></td>
                                    <td><?= $stat['receptions'] ?? '' ?></td>
                                <?php endif; ?>
                                <td>
                                    <?php
                                        $fp = 0;
                                        if ($position === 'qb') {
                                            $fp = 0.04 * ($stat['pass_yards'] ?? 0)
                                                + 4 * ($stat['pass_tds'] ?? 0)
                                                - 1 * ($stat['interceptions'] ?? 0)
                                                + 0.1 * ($stat['rush_yards'] ?? 0)
                                                + 6 * ($stat['rush_tds'] ?? 0);
                                        } else {
                                            $fp = 0.1 * ($stat['rush_yards'] ?? 0)
                                                + 6 * ($stat['rush_tds'] ?? 0)
                                                + 0.1 * ($stat['rec_yards'] ?? 0)
                                                + 6 * ($stat['rec_tds'] ?? 0)
                                                + 1 * ($stat['receptions'] ?? 0);
                                        }
                                        echo round($fp, 2);
                                    ?>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>

    <?php if ($predictions): ?>
        <div class="card">
            <div class="card-header bg-primary text-white">🔮 2025 Projections</div>
            <div class="card-body">
                <ul class="list-group list-group-flush">
                    <?php if ($position === 'qb'): ?>
                        <li class="list-group-item"><strong>Pass Yards:</strong> <?= $predictions['Predicted_PassYards_2025'] ?></li>
                        <li class="list-group-item"><strong>Pass TDs:</strong> <?= $predictions['Predicted_PassTDs_2025'] ?></li>
                        <li class="list-group-item"><strong>Rush Yards:</strong> <?= $predictions['Predicted_RushYards_2025'] ?></li>
                        <li class="list-group-item"><strong>Rush TDs:</strong> <?= $predictions['Predicted_RushTDs_2025'] ?></li>
                        <li class="list-group-item"><strong>Fantasy Points:</strong> <?= $predictions['PredictedFantasyPts_2025'] ?></li>
                    <?php else: ?>
                        <li class="list-group-item"><strong>Rush Yards:</strong> <?= $predictions['Predicted_RushYards_2025'] ?? '' ?></li>
                        <li class="list-group-item"><strong>Rush TDs:</strong> <?= $predictions['Predicted_RushTDs_2025'] ?? '' ?></li>
                        <li class="list-group-item"><strong>Rec Yards:</strong> <?= $predictions['Predicted_RecYards_2025'] ?? '' ?></li>
                        <li class="list-group-item"><strong>Rec TDs:</strong> <?= $predictions['Predicted_RecTDs_2025'] ?? '' ?></li>
                        <li class="list-group-item"><strong>Receptions:</strong> <?= $predictions['Predicted_Receptions_2025'] ?? '' ?></li>
                        <li class="list-group-item"><strong>Fantasy Points:</strong> <?= $predictions['PredictedFantasyPts_2025'] ?? '' ?></li>
                    <?php endif; ?>
                </ul>
            </div>
        </div>
    <?php else: ?>
        <p class="mt-3">No 2025 predictions found.</p>
    <?php endif; ?>
</div>
</body>
</html>

<?php $conn->close(); ?>
