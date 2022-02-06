const btn = document.querySelector('.btn');

btn.addEventListener('click', (e) => {
    e.preventDefault();  // 禁止默认操作
    console.log('click');
    window.location.href = "./limit.html";
});







