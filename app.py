import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌깨기 게임",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 벽돌깨기")
st.caption("← → 키로 패들을 움직이세요!")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
    body {
        margin: 0;
        background: #111827;
        color: white;
        font-family: Arial, sans-serif;
        text-align: center;
    }

    #gameCanvas {
        background: #0f172a;
        border: 3px solid #38bdf8;
        border-radius: 10px;
        max-width: 100%;
    }

    .info {
        display: flex;
        justify-content: space-around;
        margin: 10px auto;
        max-width: 500px;
        font-size: 18px;
        font-weight: bold;
    }

    button {
        background: #38bdf8;
        color: #082f49;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
    }

    button:hover {
        background: #7dd3fc;
    }

    #message {
        font-size: 24px;
        font-weight: bold;
        margin: 10px;
        height: 30px;
    }
</style>
</head>

<body>

<div class="info">
    <div>점수: <span id="score">0</span></div>
    <div>목숨: <span id="lives">3</span></div>
    <div>레벨: <span id="level">1</span></div>
</div>

<canvas id="gameCanvas" width="500" height="500"></canvas>

<div id="message"></div>

<button onclick="restartGame()">🔄 다시 시작</button>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const scoreElement = document.getElementById("score");
const livesElement = document.getElementById("lives");
const levelElement = document.getElementById("level");
const messageElement = document.getElementById("message");

let score = 0;
let lives = 3;
let level = 1;

let gameRunning = true;

let ball = {
    x: canvas.width / 2,
    y: canvas.height - 60,
    dx: 3,
    dy: -3,
    radius: 8
};

let paddle = {
    width: 90,
    height: 12,
    x: canvas.width / 2 - 45,
    speed: 7
};

let rightPressed = false;
let leftPressed = false;

const brickRows = 5;
const brickColumns = 8;

const brickWidth = 52;
const brickHeight = 20;
const brickPadding = 8;
const brickOffsetTop = 50;
const brickOffsetLeft = 18;

let bricks = [];

function createBricks() {
    bricks = [];

    for (let row = 0; row < brickRows; row++) {
        bricks[row] = [];

        for (let col = 0; col < brickColumns; col++) {
            bricks[row][col] = {
                x: 0,
                y: 0,
                alive: true,
                color: getBrickColor(row)
            };
        }
    }
}

function getBrickColor(row) {
    const colors = [
        "#ef4444",
        "#f97316",
        "#eab308",
        "#22c55e",
        "#3b82f6"
    ];

    return colors[row % colors.length];
}

function drawBall() {
    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        ball.radius,
        0,
        Math.PI * 2
    );

    ctx.fillStyle = "#ffffff";
    ctx.fill();

    ctx.closePath();
}

function drawPaddle() {
    ctx.beginPath();

    ctx.roundRect(
        paddle.x,
        canvas.height - paddle.height - 15,
        paddle.width,
        paddle.height,
        6
    );

    ctx.fillStyle = "#38bdf8";
    ctx.fill();

    ctx.closePath();
}

function drawBricks() {

    for (let row = 0; row < brickRows; row++) {

        for (let col = 0; col < brickColumns; col++) {

            const brick = bricks[row][col];

            if (!brick.alive) {
                continue;
            }

            const brickX =
                col * (brickWidth + brickPadding)
                + brickOffsetLeft;

            const brickY =
                row * (brickHeight + brickPadding)
                + brickOffsetTop;

            brick.x = brickX;
            brick.y = brickY;

            ctx.beginPath();

            ctx.roundRect(
                brickX,
                brickY,
                brickWidth,
                brickHeight,
                4
            );

            ctx.fillStyle = brick.color;
            ctx.fill();

            ctx.closePath();
        }
    }
}

function draw() {

    if (!gameRunning) {
        return;
    }

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    drawBricks();
    drawBall();
    drawPaddle();

    collisionDetection();

    // 벽 충돌
    if (
        ball.x + ball.dx >
        canvas.width - ball.radius ||

        ball.x + ball.dx <
        ball.radius
    ) {
        ball.dx = -ball.dx;
    }

    if (
        ball.y + ball.dy <
        ball.radius
    ) {
        ball.dy = -ball.dy;
    }

    // 바닥 충돌
    if (
        ball.y + ball.dy >
        canvas.height - ball.radius
    ) {

        const paddleY =
            canvas.height -
            paddle.height -
            15;

        if (
            ball.x >= paddle.x &&
            ball.x <= paddle.x + paddle.width &&
            ball.y < paddleY + paddle.height
        ) {

            // 패들의 어느 위치를 맞혔는지에 따라 각도 변경
            let hitPosition =
                (ball.x - paddle.x) /
                paddle.width;

            let angle =
                (hitPosition - 0.5) * Math.PI / 2;

            const speed =
                Math.sqrt(
                    ball.dx * ball.dx +
                    ball.dy * ball.dy
                );

            ball.dx =
                speed * Math.sin(angle);

            ball.dy =
                -Math.abs(
                    speed * Math.cos(angle)
                );

        } else {

            lives--;

            livesElement.textContent = lives;

            if (lives <= 0) {
                gameOver();
                return;
            }

            resetBall();
        }
    }

    // 패들 이동
    if (rightPressed) {
        paddle.x += paddle.speed;
    }

    if (leftPressed) {
        paddle.x -= paddle.speed;
    }

    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (
        paddle.x + paddle.width >
        canvas.width
    ) {
        paddle.x =
            canvas.width - paddle.width;
    }

    ball.x += ball.dx;
    ball.y += ball.dy;

    requestAnimationFrame(draw);
}

function collisionDetection() {

    let remainingBricks = 0;

    for (let row = 0; row < brickRows; row++) {

        for (let col = 0; col < brickColumns; col++) {

            const brick = bricks[row][col];

            if (!brick.alive) {
                continue;
            }

            remainingBricks++;

            if (
                ball.x > brick.x &&
                ball.x <
                    brick.x + brickWidth &&

                ball.y > brick.y &&
                ball.y <
                    brick.y + brickHeight
            ) {

                ball.dy = -ball.dy;

                brick.alive = false;

                score += 10;

                scoreElement.textContent = score;
            }
        }
    }

    if (remainingBricks === 0) {

        if (level < 3) {

            level++;

            levelElement.textContent = level;

            resetBall();
            createBricks();

        } else {

            gameClear();
        }
    }
}

function resetBall() {

    ball.x = canvas.width / 2;
    ball.y = canvas.height - 60;

    const direction =
        Math.random() > 0.5 ? 1 : -1;

    ball.dx = 3 * direction;
    ball.dy = -3;

    paddle.x =
        canvas.width / 2 -
        paddle.width / 2;
}

function gameOver() {

    gameRunning = false;

    messageElement.textContent =
        "💥 게임 오버!";

}

function gameClear() {

    gameRunning = false;

    messageElement.textContent =
        "🎉 게임 클리어!";
}

function restartGame() {

    score = 0;
    lives = 3;
    level = 1;

    scoreElement.textContent = score;
    livesElement.textContent = lives;
    levelElement.textContent = level;

    messageElement.textContent = "";

    gameRunning = true;

    createBricks();
    resetBall();

    draw();
}

document.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "ArrowRight" ||
            event.key === "d"
        ) {
            rightPressed = true;
        }

        if (
            event.key === "ArrowLeft" ||
            event.key === "a"
        ) {
            leftPressed = true;
        }
    }
);

document.addEventListener(
    "keyup",
    function(event) {

        if (
            event.key === "ArrowRight" ||
            event.key === "d"
        ) {
            rightPressed = false;
        }

        if (
            event.key === "ArrowLeft" ||
            event.key === "a"
        ) {
            leftPressed = false;
        }
    }
);

// 모바일 터치 조작
canvas.addEventListener(
    "touchmove",
    function(event) {

        event.preventDefault();

        const rect =
            canvas.getBoundingClientRect();

        const touch =
            event.touches[0];

        const scale =
            canvas.width / rect.width;

        paddle.x =
            (touch.clientX - rect.left) * scale
            - paddle.width / 2;

        if (paddle.x < 0) {
            paddle.x = 0;
        }

        if (
            paddle.x + paddle.width >
            canvas.width
        ) {
            paddle.x =
                canvas.width - paddle.width;
        }
    },
    { passive: false }
);

createBricks();
draw();

</script>

</body>
</html>
"""

components.html(
    game_html,
    height=600,
    scrolling=False
)
