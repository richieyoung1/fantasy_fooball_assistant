<?php
// Database config
$host = 'localhost';
$user = 'root';
$pass = 'Richie30';
$db = 'fantasy_football';

// Connect to MySQL
$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die("❌ Connection failed: " . $conn->connect_error);
}

// Dropdown setup
$positions = ['qb', 'rb', 'wr', 'te'];
$years = range(2020, 2025);
$selected_pos = $_GET['position'] ?? 'qb';
$selected_year = $_GET['year'] ?? 2024;
$table = "{$selected_pos}_{$selected_year}_stats";

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
    <title>Fantasy Football Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: #f2f4f7;
            color: #333;
            padding: 30px;
        }
        h1 {
            font-weight: 600;
            margin-bottom: 20px;
        }
        form {
            margin-bottom: 20px;
        }
        select, button {
            padding: 8px 12px;
            margin-right: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            background-color: #007BFF;
            color: white;
            cursor: pointer;
            transition: 0.3s;
        }
        button:hover {
            background-color: #0056b3;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.05);
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
    </style>
</head>
<body>
<p>
    <?php include 'nav_bar.php'; ?>


</p>

    <h1>Fantasy Football Stats Viewer</h1>

    <form method="get">
        <label>Position:
            <select name="position">
                <?php foreach ($positions as $pos): ?>
                    <option value="<?= $pos ?>" <?= $selected_pos == $pos ? 'selected' : '' ?>><?= strtoupper($pos) ?></option>
                <?php endforeach; ?>
            </select>
        </label>

        <label>Year:
            <select name="year">
                <?php foreach ($years as $year): ?>
                    <option value="<?= $year ?>" <?= $selected_year == $year ? 'selected' : '' ?>>
                        <?= $year ?><?= $year == 2025 ? ' (Predicted)' : '' ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </label>

        <button type="submit">View Stats</button>
    </form>

    <?php if ($valid_table): ?>
        <h2><?= strtoupper($selected_pos) ?> Stats for <?= $selected_year ?> <?= $selected_year == 2025 ? "(Predicted)" : "" ?></h2>
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
                $order_by = $selected_year == 2025 ? "ORDER BY PredictedFantasyPts_2025 DESC" : "";
                $res = $conn->query("SELECT * FROM `$table` $order_by LIMIT 100");
                
                while ($row = $res->fetch_assoc()) {
                    echo "<tr>";

                    // Image lookup
                    $name = strtolower(str_replace([' ', '.', "'"], '_', $row['Player'])) . ".png";
                    echo "<td><img src='images/$name' onerror=\"this.onerror=null;this.src='images/default.png';\" alt='photo'></td>";

                    // Table data
                    foreach ($row as $key => $val) {
                        // Make the 'Player' column clickable with position
                        if (strtolower($key) === 'player') {
                            $playerLink = "player.php?player=" . urlencode($val) . "&position=" . urlencode($selected_pos);
                            echo "<td><a href='$playerLink'>" . htmlspecialchars($val) . "</a></td>";
                        } else {
                            echo "<td>" . htmlspecialchars($val ?? '') . "</td>";
                        }
                    }
                    
                    
                    
                    

                    echo "</tr>";
                }
                ?>
            </tbody>
        </table>
    <?php else: ?>
        <p>⚠️ Table <strong><?= $table ?></strong> does not exist in the database.</p>
    <?php endif; ?>
</body>
</html>
