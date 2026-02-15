/**
 * RESTAURANT MANAGEMENT SYSTEM - MAIN LOGIC
 * Handles: Cart, Toasts, and Backend Synchronization
 */

// 1. Initialize Cart from LocalStorage
let cart = JSON.parse(localStorage.getItem('restaurantCart')) || [];

// 2. Core Cart Functions
function addToCart(id, name, price) {
    const item = { 
        id: id, 
        name: name, 
        price: parseFloat(price) 
    };
    
    cart.push(item);
    syncCart();
    
    // UI Feedback
    showToast(`${name} added to your order!`);
    updateCartCount();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    syncCart();
    updateCartCount();
    
    // If we are on the cart page, refresh the list dynamically
    if (window.location.pathname.includes('cart')) {
        renderCartPage();
    }
}

function syncCart() {
    localStorage.setItem('restaurantCart', JSON.stringify(cart));
}

// 3. UI Update Functions
function updateCartCount() {
    const countBadge = document.getElementById('cart-count');
    if (countBadge) {
        countBadge.innerText = cart.length;
        // Visual "pop" effect
        countBadge.style.transform = "scale(1.2)";
        setTimeout(() => countBadge.style.transform = "scale(1)", 200);
    }
}

function showToast(message) {
    const toastElement = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toast-message');
    
    if (toastElement) {
        toastMessage.innerText = message;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    }
}

// 4. Backend Integration (The "Real-Life" Part)
async function placeOrder() {
    if (cart.length === 0) {
        showToast("Your cart is empty!");
        return;
    }

    const orderButton = document.getElementById('place-order-btn');
    if(orderButton) orderButton.disabled = true;

    try {
        const response = await fetch('/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ items: cart })
        });

        const result = await response.json();

        if (response.ok) {
            showToast("Order placed successfully!");
            cart = [];
            syncCart();
            updateCartCount();
            
            // REDIRECT logic: Move to the success bill page using the order_id from backend
            setTimeout(() => { 
                window.location.href = '/success/' + result.order_id; 
            }, 1000);

        } else {
            showToast("Error: " + result.message);
        }
    } catch (error) {
        console.error("Order Error:", error);
        showToast("Server error. Please try again later.");
    } finally {
        if(orderButton) orderButton.disabled = false;
    }
}

// 5. Cart Page Rendering (If user is on cart.html)
function renderCartPage() {
    const container = document.getElementById('cart-items-container');
    const totalElement = document.getElementById('cart-total-price');
    
    if (!container) return; // Not on the cart page

    if (cart.length === 0) {
        container.innerHTML = '<div class="text-center py-5"><h3>Your cart is empty</h3><a href="/menu" class="btn btn-warning mt-3">Go to Menu</a></div>';
        if(totalElement) totalElement.innerText = "0.00";
        return;
    }

    let html = '';
    let total = 0;

    cart.forEach((item, index) => {
        total += item.price;
        html += `
            <div class="d-flex justify-content-between align-items-center border-bottom py-3">
                <div>
                    <h5 class="mb-0">${item.name}</h5>
                    <small class="text-muted">$${item.price.toFixed(2)}</small>
                </div>
                <button onclick="removeFromCart(${index})" class="btn btn-sm btn-outline-danger">
                    <i class="bi bi-trash"></i> Remove
                </button>
            </div>
        `;
    });

    container.innerHTML = html;
    if(totalElement) totalElement.innerText = total.toFixed(2);
}

// 6. Printing Function
function printBill() {
    window.print();
}

// 7. Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
    if (window.location.pathname.includes('cart')) {
        renderCartPage();
    }
});