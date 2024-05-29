const socket = io();

/**
 * Hide submit button and show captcha web component
 */
const renderCaptcha = () =>  {
    socket.emit("getCaptcha", response => {
        console.log(JSON.stringify(response));
        document.querySelectorAll('altcha-widget').forEach(c => c.remove());
        const captcha = document.createElement('altcha-widget');
        captcha.challengejson = JSON.stringify(response);
        captcha.hidelogo = "1";
        captcha.hidefooter = "1";
        captcha.style = '--altcha-max-width: 100%;';
        captcha.strings = JSON.stringify({
            label: '🤖 Bip boup ...',
            verifying: '⚙️ Vérification ...'
        });
        captcha.addEventListener('verified', event => {
            submitCaptcha(event.detail.payload);
        });

        document.querySelector('#submit button').classList.add('visually-hidden');
        document.getElementById('submit').appendChild(captcha);
    });
}

/**
 * Submit captcha payload, if successfull delete the web component and show the submit button
 * @param {string} payload 
 */
const submitCaptcha = (payload) => {
    socket.emit("submitCaptcha", payload, response => {
        if (response) {
            document.querySelector('#submit altcha-widget').remove();
            document.querySelector('#submit button').classList.remove('visually-hidden');
        } else {
            alert("Le captcha est invalid");
        }
    });
}

socket.on('connect', () => {
    console.log('Socket is connected');
    renderCaptcha();
});

socket.on('disconnect', () => {
    console.log('Socket is disconnected');
});

const form = document.querySelector('form');
const logs = document.querySelector('#logs pre');

socket.on('log', log => logs.append(log + '\n'));

const renderScreenshot = (type, png) => {
    const blob = new Blob([png]);
    const img = document.querySelector(`#${type}-screen img`);
    img.src = URL.createObjectURL(blob);
    img.onload = () => URL.revokeObjectURL(img);
    document.querySelector(`#${type}-screen .spinner`).classList.add('visually-hidden');
}

socket.on('pre-screenshot', png => renderScreenshot('pre', png));
socket.on('post-screenshot', png => renderScreenshot('post', png));

form.onsubmit = e => {
    e.preventDefault();

    document.querySelector('#submit button').disabled = 1;
    document.getElementById('spinner').classList.remove('visually-hidden');
    document.querySelector('#pre-screen .spinner').classList.remove('visually-hidden');
    document.querySelector('#post-screen .spinner').classList.remove('visually-hidden');
    document.getElementById('screenshots').classList.remove('visually-hidden');

    const apk = document.querySelector('input').files[0];
    socket.emit('submitApk', apk, status => {
        delete document.querySelector('#submit button').removeAttribute('disabled');
        document.getElementById('spinner').classList.add('visually-hidden');
        renderCaptcha();
    });
}