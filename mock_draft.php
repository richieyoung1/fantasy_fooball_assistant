<?php
// mock_draft.php
?>

<!DOCTYPE html>
<html>
<head>
    <title>Mock Draft Setup</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="bg-light">

<div class="container mt-5">
    <h2 class="mb-4">🧠 Mock Draft Simulator Setup</h2>
    <form method="post" action="start_draft.php" class="bg-white p-4 rounded shadow-sm">

        <div class="mb-3">
            <label class="form-label">Number of Teams</label>
            <input type="number" name="teams" class="form-control" min="2" max="16" value="10" required>
        </div>

        <div class="mb-3">
            <label class="form-label">Draft Format</label>
            <select name="format" class="form-select" required>
                <option value="snake">Snake</option>
                <option value="linear">Linear</option>
            </select>
        </div>

        <div class="mb-3">
            <label class="form-label">Scoring Format</label>
            <select name="scoring" class="form-select" required>
                <option value="standard">Standard (no PPR)</option>
                <option value="half_ppr">Half-PPR</option>
                <option value="full_ppr" selected>Full PPR</option>
            </select>
        </div>

        <h5 class="mt-4">Starting Lineup</h5>
        <div class="row">
            <div class="col-md-2">
                <label class="form-label">QB</label>
                <input type="number" name="qb" class="form-control" min="0" value="1" required>
            </div>
            <div class="col-md-2">
                <label class="form-label">RB</label>
                <input type="number" name="rb" class="form-control" min="0" value="2" required>
            </div>
            <div class="col-md-2">
                <label class="form-label">WR</label>
                <input type="number" name="wr" class="form-control" min="0" value="2" required>
            </div>
            <div class="col-md-2">
                <label class="form-label">TE</label>
                <input type="number" name="te" class="form-control" min="0" value="1" required>
            </div>
            <div class="col-md-2">
                <label class="form-label">FLEX</label>
                <input type="number" name="flex" class="form-control" min="0" value="1" required>
            </div>
            <div class="col-md-2">
                <label class="form-label">Bench</label>
                <input type="number" name="bench" class="form-control" min="0" value="6" required>
            </div>
        </div>

        <div class="mt-4 text-end">
            <a href="index.php" class="btn btn-secondary">← Back to Dashboard</a>
            <a href="mock_draft_start.php" class="btn btn-primary">🏈 Start Mock Draft</a>

        </div>
    </form>
</div>

</body>
</html>
