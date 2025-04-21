<?php
$host = 'localhost';
$user = 'root';
$pass = 'Richie30';
$db = 'fantasy_football';

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die("❌ Connection failed: " . $conn->connect_error);
}

// Options
$positions = ['qb', 'rb', 'wr', 'te'];
$years = range(2020, 2025);
$year = $_GET['year'] ?? 2024;
$pos = $_GET['position'] ?? 'qb';
$table = "{$pos}_{$year}_stats";

// Load player names from CSV
$team_players = [];
if (($handle = fopen("players.csv", "r")) !== false) {
    while (($row = fgetcsv($handle, 0, ",", '"', "\\")) !== false) {

        $team_players[] = strtolower(trim($row[0]));
    }
    fclose($handle);
}

// Check if table exists
$tables = [];
$result = $conn->query("SHOW TABLES");
while ($row = $result->fetch_array()) {
    $tables[] = $row[0];
}
$valid_table = in_array($table, $tables);
?>

<!DOCTYPE html>
<html>
<head>
    <title>My Fantasy Team</title>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: #f2f4f7;
            color: #333;
            padding: 30px;
        }
        h1, h2 {
            font-weight: 600;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.05);
            margin-top: 20px;
        }
        th {
            background: #007BFF;
            color: white;
            padding: 10px;
            text-align: left;
        }
        td {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        tr:nth-child(even) {
            background: #f9f9f9;
        }
        img {
            border-radius: 50%;
            width: 40px;
            height: 40px;
            object-fit: cover;
        }
        form {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>📋 My Fantasy Team - <?= strtoupper($pos) ?> - <?= $year ?> <?= $year == 2025 ? "(Predicted)" : "" ?></h1>

    <form method="get">
        <label>Position:
            <select name="position">
                <?php foreach ($positions as $p): ?>
                    <option value="<?= $p ?>" <?= $p == $pos ? 'selected' : '' ?>><?= strtoupper($p) ?></option>
                <?php endforeach; ?>
            </select>
        </label>

        <label>Year:
            <select name="year">
                <?php foreach ($years as $y): ?>
                    <option value="<?= $y ?>" <?= $y == $year ? 'selected' : '' ?>>
                        <?= $y ?><?= $y == 2025 ? " (Predicted)" : "" ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </label>

        <button type="submit">View Team Stats</button>
    </form>

    <?php if ($valid_table): ?>
        <table>
            <thead>
                <tr>
                    <th>Photo</th>
                    <?php
                    $res = $conn->query("SELECT * FROM `$table` LIMIT 1");
                    while ($field = $res->fetch_field()) {
                        echo "<th>{$field->name}</th>";
                    }
                    ?>
                </tr>
            </thead>
            <tbody>
                <?php
                $res = $conn->query("SELECT * FROM `$table`");
                while ($row = $res->fetch_assoc()) {
                    $name_key = strtolower(trim($row['Player']));
                    if (!in_array($name_key, $team_players)) continue;

                    echo "<tr>";
                    $img_name = strtolower(str_replace([' ', '.', "'"], '_', $row['Player'])) . ".png";
                    echo "<td><img src='images/$img_name' onerror=\"this.onerror=null;this.src='images/default.png';\"></td>";

                    foreach ($row as $val) {
                        echo "<td>" . htmlspecialchars($val ?? '') . "</td>";
                    }
                    echo "</tr>";
                }
                ?>
            </tbody>
        </table>
    <?php else: ?>
        <p>⚠️ No stats available for <?= $pos ?> in <?= $year ?>.</p>
    <?php endif; ?>
</body>
</html>
