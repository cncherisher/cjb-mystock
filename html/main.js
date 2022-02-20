// div3

const d3 = document.querySelector('#d3')
const disciplineBtn = document.querySelector('#disciplineBtn');
let d3InsFlag = 0;

disciplineBtn.addEventListener('click', (e) => {
    e.preventDefault();  // 禁止默认操作
    console.log('click disciplineBtn');
    if (d3InsFlag == 0) {
        const p = document.createElement('p');
        const ta = document.createElement('textarea');
        ta.setAttribute("rows", "5");
        ta.setAttribute("cols", "50");
        ta.setAttribute("disabled", "True");
        ta.appendChild(document.createTextNode(
            "1. aaaa\n" +
            "2. bbbb\n" +
            "3. cccc"
        ));
        p.appendChild(ta)
        d3.appendChild(p);
        d3InsFlag = 1;
    }    
});



