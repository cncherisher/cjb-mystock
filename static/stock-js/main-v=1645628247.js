const fundCodeForm = document.querySelector('#fundCodeForm');
const fundCodeInput = document.querySelector('#fundCodeInput');
let fundCodeErrorFlag = 0;

fundCodeInput.addEventListener('input', (e) => {
    e.preventDefault();  // 禁止默认操作
    console.log('oninput');

    const v = fundCodeInput.value;
    const l = v.length;
    const c = v[l-1];
    
    if (l < 6) {
        document.querySelector('#fundCodeSubmit').disabled = true;
    } else {
        document.querySelector('#fundCodeSubmit').disabled = false;
    }

    if ((c < '0' || c > '9') && (c !== '')) {
        fundCodeInput.value = v.substring(0, l-1);
        if (fundCodeErrorFlag === 0) {
            const d = document.createElement('div');
            d.setAttribute("class", "alert alert-danger");
            d.appendChild(document.createTextNode("请输入数字！"));
            fundCodeForm.parentNode.insertBefore(d, fundCodeForm);
            fundCodeErrorFlag = 1;
        }
    } else if (fundCodeErrorFlag === 1) {
        const d = document.querySelector('.alert-danger');
        d.remove();
        fundCodeErrorFlag = 0;
    }
});


