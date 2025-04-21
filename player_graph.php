<?php
// --- DB CONFIG ---
$host = 'localhost';
$user = 'root';
$pass = 'Richie30';
$db = 'fantasy_football';
$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) die("DB connection failed.");

// --- Form Values ---
$player = $_GET['player'] ?? '';
$stats = $_GET['stats'] ?? [];
$chartType = $_GET['chart_type'] ?? 'bar';

$available_stats = ['Yards', 'Touchdowns', 'Interceptions', 'Completions', 'Attempts', 'Rush_Yards', 'Passer_Rating'];

// --- Fetch stat values ---
$stat_values_2024 = $stat_values_2025 = [];
if ($player && $stats) {
    $player_safe = $conn->real_escape_string($player);

    $res2024 = $conn->query("SELECT * FROM qb_2024_stats WHERE LOWER(Player) = LOWER('$player_safe') LIMIT 1");
    $res2025 = $conn->query("SELECT * FROM qb_2025_stats WHERE LOWER(Player) = LOWER('$player_safe') LIMIT 1");

    if ($res2024 && $row = $res2024->fetch_assoc()) {
        foreach ($stats as $stat) {
            $stat_values_2024[] = $row[$stat] ?? 0;
        }
    }
    if ($res2025 && $row = $res2025->fetch_assoc()) {
        foreach ($stats as $stat) {
            $stat_values_2025[] = $row[$stat] ?? 0;
        }
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Player Stat Graph</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Inter', sans-serif; padding: 30px; background: #f7f9fc; }
        h1 { font-size: 26px; margin-bottom: 20px; }
        label, select, input[type="checkbox"] { margin-right: 15px; }
        button { padding: 8px 15px; background: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }
        canvas { margin-top: 30px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 0 10px rgba(0,0,0,0.05); }
    </style>
</head>
<body>
    <h1>📊 Player Stat Graph</h1>

    <form method="get">
        <label>
            Player:
            <select name="player">
                <option value="">-- Select Player --</option>
                <?php
                $res = $conn->query("SELECT DISTINCT Player FROM qb_2024_stats ORDER BY Player");
                while ($row = $res->fetch_assoc()) {
                    $p = $row['Player'];
                    $sel = strtolower($p) == strtolower($player) ? 'selected' : '';
                    echo "<option value=\"$p\" $sel>$p</option>";
                }
                ?>
            </select>
        </label>

        <label>
            Chart Type:
            <select name="chart_type">
                <?php foreach (['bar', 'line', 'pie', 'radar'] as $type): ?>
                    <option value="<?= $type ?>" <?= $chartType == $type ? 'selected' : '' ?>><?= ucfirst($type) ?></option>
                <?php endforeach; ?>
            </select>
        </label>

        <div style="margin-top: 10px;">
            <strong>Select Stats:</strong><br>
            <?php foreach ($available_stats as $stat): ?>
                <label>
                    <input type="checkbox" name="stats[]" value="<?= $stat ?>" <?= in_array($stat, $stats) ? 'checked' : '' ?>>
                    <?= str_replace('_', ' ', $stat) ?>
                </label>
            <?php endforeach; ?>
        </div>

        <button type="submit">Show Graph</button>
    </form>

    <?php if ($player && $stats): ?>
        <h2>📈 <?= htmlspecialchars($player) ?> - 2024 vs 2025</h2>
        <canvas id="myChart" width="800" height="400"></canvas>
        <script>
        const ctx = document.getElementById('myChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: '<?= $chartType ?>',
            data: {
                labels: <?= json_encode($stats) ?>,
                datasets: [
                    {
                        label: '2024 Actual',
                        backgroundColor: '#007bff',
                        data: <?= json_encode($stat_values_2024) ?>
                    },
                    {
                        label: '2025 Predicted',
                        backgroundColor: '#28a745',
                        data: <?= json_encode($stat_values_2025) ?>
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '<?= addslashes($player) ?> - <?= ucfirst($chartType) ?> Chart'
                    }
                }
            }
        });
        </script>
    <?php endif; ?>
</body>
</html>
