

document.getElementById("loginform").addEventListener("submit", function(event) {
    event.preventDefault();
    login();
});

document.getElementById("submit").addEventListener("click", function(event) {
	event.preventDefault();
	login();
});

function login() {
    var username = document.getElementById("email").value;
    var password = document.getElementById("password").value;
    var data = {
        username: username,
        password: password
    };

    fetch("/api/login.php", {
        method: "POST",
        body: new URLSearchParams(data),
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        }
    }).then(response => {
        response.json().then(data => {
            if(data["status"] === "success") {
                window.location.href = "/home.php";
            } else {
                alert(data["status"]);
            }
        })
    });
}
