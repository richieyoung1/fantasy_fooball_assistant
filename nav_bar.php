<!-- nav_bar.php -->
<style>
    .navbar {
        background-color: #007BFF;
        padding: 15px 30px;
        display: flex;
        gap: 30px;
        align-items: center;
        font-family: 'Inter', sans-serif;
    }

    .navbar a {
        color: white;
        font-weight: 600;
        text-decoration: none;
        font-size: 16px;
        transition: 0.3s ease;
    }

    .navbar a:hover {
        text-decoration: underline;
        opacity: 0.9;
    }

    @media (max-width: 600px) {
        .navbar {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
        }
    }
</style>

<nav class="navbar">
    <a href="index.php">🏠 Dashboard</a>
    <a href="sleeper_team.php">🛏️ My Fantasy Team</a>
    <a href="mock_draft_start.php">🧠 Start Mock Draft</a>
</nav>
