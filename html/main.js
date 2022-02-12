const limitBtn = document.querySelector('#limitBtn');

limitBtn.addEventListener('click', (e) => {
    e.preventDefault();  // 禁止默认操作
    console.log('click');
    window.location.href = "./limit.html";
});


const FundBtn = document.querySelector('#FundBtn');

FundBtn.addEventListener('click', (e) => {
    e.preventDefault();  // 禁止默认操作
    console.log('click');
    window.location.href = "./test";
});





