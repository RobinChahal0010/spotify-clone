document.addEventListener("DOMContentLoaded", function () {
    // Check previous theme
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
    }
});

function toggleTheme() {
    document.body.classList.toggle("dark-mode");

    // Save theme in localStorage
    if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
    } else {
        localStorage.setItem("theme", "light");
    }
}

