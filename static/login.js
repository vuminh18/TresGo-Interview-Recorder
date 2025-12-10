document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.querySelector('.login-button');
    
    // --- SỬA LẠI ĐOẠN NÀY ĐỂ BẮT ĐÚNG Ô NHẬP ---
    const tokenInput = document.getElementById('token-input');
    const nameInput = document.getElementById('name-input');
    // -------------------------------------------
    
    const errorMessage = document.getElementById('error-message');

    const displayError = (message) => {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    };

    const clearError = () => {
        errorMessage.classList.add('hidden');
        errorMessage.textContent = '';
    };

    const setButtonLoading = (isLoading) => {
        if (isLoading) {
            loginButton.disabled = true;
            loginButton.textContent = 'Verifying...';
        } else {
            loginButton.disabled = false;
            loginButton.textContent = 'LOG IN';
        }
    };

    loginButton.addEventListener('click', async (e) => {
        e.preventDefault();
        clearError();

        // Kiểm tra xem input có tìm thấy không để tránh lỗi null
        if (!tokenInput || !nameInput) {
            console.error("Error: Input elements not found.");
            return;
        }

        const token = tokenInput.value.trim();
        const userName = nameInput.value.trim();

        if (!token || !userName) {
            displayError('Please enter both Token and Name.');
            return;
        }

        setButtonLoading(true);

        try {
            // 1. Verify Token [cite: 39]
            let response = await fetch('/api/verify-token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token })
            });

            if (response.status === 401) {
                displayError('Invalid Token. Please check again.');
                setButtonLoading(false);
                return;
            }

            if (!response.ok) throw new Error(`Server Error: ${response.status}`);

            // 2. Start Session [cite: 40]
            response = await fetch('/api/session/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, userName })
            });

            if (!response.ok) throw new Error('Failed to create session.');

            const sessionResult = await response.json();
            
            // 3. Save info
            localStorage.setItem('userToken', token);
            localStorage.setItem('userName', userName);
            localStorage.setItem('sessionFolder', sessionResult.folder);

            // 4. Redirect
            // Vì login.html và interview.html cùng nằm trong /static/ nên gọi thẳng tên là được
            window.location.href = '/static/interview.html';

        } catch (error) {
            console.error('Error:', error);
            displayError(`Error: ${error.message}`);
        } finally {
            setButtonLoading(false);
        }
    });
});