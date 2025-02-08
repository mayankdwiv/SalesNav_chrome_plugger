
let currentFactIndex = 0;
setInterval(() => {
    currentFactIndex = (currentFactIndex + 1) % facts.length;
    document.getElementById('fact').textContent = facts[currentFactIndex];
}, 5000); // Change fact every 5 seconds

// Function to check scraping status
// function checkStatus() {
//     fetch('/check-status')
//         .then(response => response.json())
//         .then(data => {
//             if (data.completed) {
//                 // Redirect to download.html if scraping is completed
//                 window.location.href = '/download';
//             } else if (!data.in_progress) {
//                 // Handle unexpected status (e.g., error)
//                 alert('An error occurred. Please try again.');
//             } else {
//                 // Continue polling if still in progress
//                 setTimeout(checkStatus, 3000); // Poll every 3 seconds
//             }
//         })
//         .catch(error => console.error('Error checking status:', error));
// }
function checkLink() {
fetch('/get-link')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = '/download';  // Redirect to the download page
        } else {
            setTimeout(checkLink, 2000);  // Check again after 2 seconds
        }
    })
    .catch(error => {
        console.error('Error fetching link:', error);
        setTimeout(checkLink, 2000);  // Retry on error
    });
}
// Memory Game Logic
const gameContainer = document.getElementById('memoryGame');
const cardCount = 8; // 4 pairs
let flippedCards = [];
let matchedPairs = 0;

// Create cards
const symbols = ['★', '♦', '♥', '♠'];
const cards = [...symbols, ...symbols];

// Shuffle cards
cards.sort(() => Math.random() - 0.5);

// Generate card elements
cards.forEach((symbol, index) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.symbol = symbol;
    card.dataset.index = index;
    
    card.addEventListener('click', () => flipCard(card));
    gameContainer.appendChild(card);
});

function flipCard(card) {
    if (flippedCards.length === 2 || card.classList.contains('flipped')) return;

    card.classList.add('flipped');
    card.textContent = card.dataset.symbol;
    flippedCards.push(card);

    if (flippedCards.length === 2) {
        setTimeout(checkMatch, 500);
    }
}

function checkMatch() {
    const [card1, card2] = flippedCards;
    if (card1.dataset.symbol === card2.dataset.symbol) {
        matchedPairs++;
        if (matchedPairs === symbols.length) {
            setTimeout(() => {
                resetGame();
            }, 1000);
        }
    } else {
        card1.classList.remove('flipped');
        card2.classList.remove('flipped');
        card1.textContent = '';
        card2.textContent = '';
    }
    flippedCards = [];
}

function resetGame() {
    matchedPairs = 0;
    const cards = gameContainer.querySelectorAll('.card');
    cards.forEach(card => {
        card.classList.remove('flipped');
        card.textContent = '';
    });
    // Reshuffle
    Array.from(cards).sort(() => Math.random() - 0.5)
        .forEach(card => gameContainer.appendChild(card));
}

window.onload = checkLink;