async function redirectToSellerPage(sellerId) {
    try {
        const response = await fetch(`/api/user/${sellerId}/email`);
        const data = await response.json();
        if (data.error) {
            console.error('Error:', data.error);
            return;
        }
        
        const emailBytes = new TextEncoder().encode(data.email);
        const hashBuffer = await crypto.subtle.digest('SHA-256', emailBytes);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        
        window.location.href = `/user/${hashHex}`;
    } catch (error) {
        console.error('Error:', error);
    }
} 