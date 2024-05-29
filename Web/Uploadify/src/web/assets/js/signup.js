
document.getElementById("signupform").addEventListener("submit", function(event) {
    event.preventDefault();
    signup();
});


function signup() {
    var username = document.getElementById("email").value;
    var password = document.getElementById("password").value;
    var data = {
        username: username,
        password: password
    };

    fetch("/api/signup.php", {
        method: "POST",
        body: new URLSearchParams(data),
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        }
    }).then(response => {
        response.json().then(data => {
            if(data["status"] == "success") {
                alert("Account created successfully!")
                window.location.href = "/login.php";
            } else {
                alert(data["status"]);
            }
        })
    });
}