// 设置全局变量
const PriceChart = document.getElementById("price_chart");
let now_tf = "m1"
let old_price = 0
let smsTimer = null;
let smsCountdown = 60;
let user_id = undefined;
let username = undefined;
let cookie_name = undefined;

let is_vip = false;

const allCookies = document.cookie;
if (allCookies){
    const [name, value] = allCookies.trim().split('=');
    cookie_name = name
    const cookie_data = value.trim().split('_');
    username = cookie_data[2]
    user_id = cookie_data[1]


    if (! (user_id && username)){
        deleteCookie(name);
    }
}else{
    console.log("allCookies:",allCookies);
}


const chart = LightweightCharts.createChart(PriceChart, {
        layout: { background: { color: "#1a1a2e" }, textColor: "#e6e6e6" },
        grid: {
            vertLines: { color: "rgba(255,255,255,0.1)" },
            horzLines: { color: "rgba(255,255,255,0.1)" }
        },
        timeScale: { borderColor: "#444" },
        rightPriceScale: { borderColor: "#444" }
    });

// 绑定 crosshair 事件
chart.subscribeCrosshairMove((param) => {

    const infoBox = document.getElementById("ohlc-info");
    // 鼠标不在图表上
    if (!param || !param.seriesData) {
        infoBox.innerHTML = "OHLC: --";
        return;
    }
    const ohlc = param.seriesData.get(candleSeries);
    if (!ohlc) {
        infoBox.innerHTML = "OHLC: --";
        return;
    }
    infoBox.innerHTML =
        `O: <span style="color:#4db6ac">${ohlc.open}</span> `
        + `H: <span style="color:#4db6ac">${ohlc.high}</span> `
        + `L: <span style="color:#ef9a9a">${ohlc.low}</span> `
        + `C: <span style="color:#ffffff">${ohlc.close}</span>`;
});

// K 线图颜色配置
const candleSeries = chart.addCandlestickSeries({
    upColor: "#4ecca3",
    downColor: "#e84545",
    borderUpColor: "#4ecca3",
    borderDownColor: "#e84545",
    wickUpColor: "#4ecca3",
    wickDownColor: "#e84545",
});

// 分时切换按键检测
const timeframeButtons = document.querySelectorAll('.timeframe-btn');
timeframeButtons.forEach(button => {
    button.addEventListener('click', function() {
        // 移除所有按钮的active类
        timeframeButtons.forEach(btn => btn.classList.remove('active'));
        // 为当前点击的按钮添加active类
        this.classList.add('active');

        // 获取时间框架
        const timeframe = this.getAttribute('data-tf');
        now_tf = timeframe
        updateTrendHeader(timeframe)
        loadKline(timeframe);
    });
});


// 删除cookie
function deleteCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}

// 切换分时效果
function loadKline(tf) {
    let data = { timeframe: tf , symbol: "XAUUSD", }
    $.ajax({
        url: "/api/kline",
        method: "GET",
        data: data,
        success: function (res) {
            const formatted = res.data.map(d => ({
                time: Math.floor(new Date(d.time).getTime() / 1000) + (3600 * 15),
                open: d.open,
                high: d.high,
                low: d.low,
                close: d.close,
            }));
            candleSeries.setData(formatted);  // 设置新的周期数据
            // 更新实时数据
            let now_price = formatted[formatted.length - 1].close

            UpNowPrice(now_price)
        }
    });
}

// 初始化K线图
function loadInitialKline() {
    loadKline("m1")
    // 自适应尺寸
    new ResizeObserver(() => {
        chart.applyOptions({
            timeScale: {
                timeVisible: true,     // 启用分钟显示
                secondsVisible: false, // 关闭秒（如果你不要秒）
            },
            width: PriceChart.clientWidth,
            height: PriceChart.clientHeight,
        });
    }).observe(PriceChart);
}

// 更新k线图数据
function UpKline(){
    loadKline(now_tf);
}

// 更新当前价格
function UpNowPrice(now_price){
    const priceElement = document.querySelector('.price');
    const changeElement = document.querySelector('.price-change');
    // 生成小幅随机价格变动
    const change = now_price - old_price
    const percentChange = (change / old_price * 100).toFixed(2);
    // 更新价格显示
    priceElement.textContent = now_price
    changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(4)} (${percentChange}%)`;

    // 根据涨跌设置颜色
    if (change > 0) {
        priceElement.className = 'price up';
        changeElement.className = 'price-change up';
    } else if (change < 0) {
        priceElement.className = 'price down';
        changeElement.className = 'price-change down';
    } else {
        priceElement.className = 'price';
        changeElement.className = 'price-change';
    }

}

// 初始化昨日收盘价
function initoldprice(){
    let data = {symbol: "XAUUSD"}
    $.ajax({
        url: "/api/old_price",
        method: "GET",
        data: data,
        success: function (res) {
            old_price = res.old_price
        }
    });
}

// 加载趋势通知
function loadNotifications() {
    let data = { timeframe: now_tf , symbol: "XAUUSD"}
    $.ajax({
        url: "/api/notifications/",
        method: "GET",
        data: data,
        success(res){
            const notificationsList = document.getElementById('notificationsList');
            notificationsList.innerHTML = '';
            res.data.forEach(notification => {
                const notificationElement = document.createElement('div');
                notificationElement.className = `notification info`;
                notificationElement.innerHTML = `
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-content">${notification.content}</div>
                    <div class="notification-time">${notification.datetime}</div>
                `;
                notificationsList.appendChild(notificationElement);
            });
        }
    })
}

// 修改趋势通知分类
function updateTrendHeader(tf) {
    const map = {
        m1: "M1",
        m5: "M5",
        m15: "M15",
        m30: "M30",
        h1: "H1"
    };

    const label = map[tf] || tf.toUpperCase();

    document.querySelector(".notifications-header").innerText = `趋势变动 (${label})`;
}

// 登陆账号
function showLogin() {
    Swal.fire({
        title: '登录账户',
        background: '#16213e',
        color: '#e6e6e6',
        scrollbarPadding: false,
        html: `
            <input id="login-username" class="swal2-input" placeholder="用户名">
            <input id="login-password" type="password" class="swal2-input" placeholder="密码">
        `,
        confirmButtonText: '登录',
        showCancelButton: true,
        cancelButtonText: '取消',
        focusConfirm: false,
        preConfirm: () => {
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;

            if (!username || !password) {
                Swal.showValidationMessage('请输入完整信息');
                return false;
            }
            return { username, password };
        }
    }).then(result => {
        if (result.isConfirmed) {
            $.ajax({
                url: "api/user_login/",
                method: "POST",
                data:result.value,
                success(res){
                    if (res.response_type === "success"){
                        Swal.fire({
                            icon: 'success',
                            title: '登录成功',
                            timer: 1500,
                            showConfirmButton: false,
                            background: '#16213e',
                            color: '#e6e6e6',
                            didClose: () => {
                                location.reload();
                            }
                        });
                    }else{
                        Swal.fire({
                            icon: 'error',
                            title: res.msg,
                            showConfirmButton: true,
                            background: '#16213e',
                            color: '#e6e6e6',
                        })
                    }

                }
            })
        }
    });
}

// 发送短信验证码
function sendSmsCode(btn) {
    const phone = document.getElementById("mobile").value;

    if (!phone) {
        Swal.fire({
            icon: 'warning',
            title: '请输入手机号后再获取验证码',
            timer: 1500,
            showConfirmButton: false,
        });
        return;
    }

    $.ajax({
        url: "api/verify_code/",
        method: "POST",
        data: {"mobile" : phone, "verify_type": "register"},
        success(res){
            if (res.response_type === "success"){
                this.$message.success('验证码已发送!');
            }
        }
    })
    // 禁用按钮并开始倒计时
    startSmsCountdown(btn);
}

// 短信发送验证码后动画
function startSmsCountdown(btn) {
    btn.disabled = true;
    btn.style.background = "#a5a5a5";
    btn.textContent = `${smsCountdown}s`;

    smsTimer = setInterval(() => {
        smsCountdown--;

        if (smsCountdown <= 0) {
            clearInterval(smsTimer);
            smsCountdown = 60;
            btn.disabled = false;
            btn.style.background = "#4ecca3";
            btn.textContent = "获取验证码";
        } else {
            btn.textContent = `${smsCountdown}s`;
        }
    }, 1000);
}

// 用户注册
function showRegister() {
    Swal.fire({
        title: '注册新账户',
        background: '#16213e',
        color: '#e6e6e6',
        scrollbarPadding: false,
        html: `
            <div style="display:flex; flex-direction:column; align-items:center; gap:10px; width:100%; margin-top:10px;">

                <input id="mobile" class="swal2-input" placeholder="手机号" style="width:90%;">
                <input id="username" class="swal2-input" placeholder="用户名" style="width:90%;">
                <input id="invite_code" class="swal2-input" placeholder="邀请码(选填)" style="width:90%;">
                <input id="password" type="password" class="swal2-input" placeholder="密码" style="width:90%;">
                <input id="repassword" type="password" class="swal2-input" placeholder="确认密码" style="width:90%;">

                <div style="display:flex; width:90%; gap:8px; align-items:center;">
                    <input id="verify_code" class="swal2-input" placeholder="短信验证码" 
                        style="width:60%; margin:0;">
                    <button id="sms-btn" 
                        class="swal2-confirm swal2-styled"
                        style="
                            width:30%;
                            height: 100%;
                            margin:0;
                            background:#4ecca3;
                            border-radius:8px;
                            font-size: 16px;
                            float: right;
                        ">
                        获取验证码
                    </button>
                </div>

            </div>
        `,
        confirmButtonText: '注册',
        showCancelButton: true,
        cancelButtonText: '取消',
        focusConfirm: false,
        didRender: () => {
            const smsBtn = document.getElementById("sms-btn");
            smsBtn.addEventListener("click", () => sendSmsCode(smsBtn));
        },
        preConfirm: () => {
            const mobile = document.getElementById('mobile').value;
            const verify_code = document.getElementById('verify_code').value;
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const password2 = document.getElementById('repassword').value;
            const invite_code = document.getElementById('invite_code').value;

            if (!mobile || !username || !password || !password2 || !verify_code) {
                Swal.showValidationMessage('请填写完整信息');
                return false;
            }
            if (password !== password2) {
                Swal.showValidationMessage('两次密码不一致');
                return false;
            }

            return { mobile, verify_code, username, password, invite_code };
        }
    }).then(result => {
        if (result.isConfirmed) {
            $.ajax({
                url: "api/user_register/",
                method: "POST",
                data : result.value,
                success(res){
                    if (res.response_type === "success"){
                        Swal.fire({
                            icon: 'success',
                            title: res.msg,
                            timer: 1500,
                            showConfirmButton: false,
                            background: '#16213e',
                            color: '#e6e6e6',
                            didClose: () => {
                                location.reload();
                            }
                        });
                    }else{
                        Swal.fire({
                            icon: 'error',
                            title: res.msg,
                            showConfirmButton: true,
                            background: '#16213e',
                            color: '#e6e6e6',
                        })
                    }
                }
            })
        }
    });
}

// 推出登陆
function logoutUser(){
    deleteCookie(cookie_name);
    location.reload();
}

// 用户状态更新
function updateUserUI(username, vip_end_time, is_vip) {
    const userSection = document.getElementById("userSection");
    if (is_vip){
        userSection.innerHTML = `
            <div class="user-info">
                <button class="recharge-btn" onclick="showRecharge()">升级会员</button>
                <span class="username">Hi, ${username}, 会员到期时间: ${vip_end_time}</span>
                <span class="logout" onclick="logoutUser()">退出</span>
            </div>
        `;
    }else{
        userSection.innerHTML = `
            <div class="user-info">
                <button class="recharge-btn" onclick="showRecharge()">升级会员</button>
                <span class="username">Hi, ${username}</span>
                <span class="logout" onclick="logoutUser()">退出</span>
            </div>
        `;
    }

}

function showRecharge() {
    Swal.fire({
        title: '选择充值时长',
        background: '#16213e',
        color: '#e6e6e6',
        confirmButtonText: '下一步',
        showCancelButton: true,
        cancelButtonText: '取消',
        html: `
                <div class="recharge-methods">
                    <div class="pay-card active"
                         data-type="day"
                         data-amount="9.9"
                         data-points="1">
                
                        <img src="/static/img/visa.svg" />
                        <span class="period">24小时</span>
                        <div class="amount">$9.9</div>
                        <div class="points">赠1 积分！</div>
                    </div>
                
                    <div class="pay-card"
                         data-type="week"
                         data-amount="29"
                         data-points="14">
                
                        <img src="/static/img/mastercard.svg" />
                        <span class="period">一周</span>
                        <div class="amount">$29</div>
                        <div class="points">赠14 积分！</div>
                    </div>
                
                    <div class="pay-card"
                         data-type="month"
                         data-amount="79"
                         data-points="90">
                
                        <img src="/static/img/bank.svg" />
                        <span class="period">一个月</span>
                        <div class="amount">$79</div>
                        <div class="points">赠90 积分！</div>
                    </div>
                    <div class="pay-card"
                         data-type="three_month"
                         data-amount="219"
                         data-points="360">
                
                        <img src="/static/img/bank.svg" />
                        <span class="period">三个月</span>
                        <div class="amount">$219</div>
                        <div class="points">赠360 积分！</div>
                    </div>
                
                    <div class="pay-card"
                         data-type="half"
                         data-amount="699"
                         data-points="1000">
                
                        <img src="/static/img/usdt.svg" />
                        <span class="period">半年</span>
                        <div class="amount">$419</div>
                        <div class="points">赠 800 积分!</div>
                    </div>
                
                    <div class="pay-card"
                         data-type="year"
                         data-amount="699"
                         data-points="1000">
                
                        <img src="/static/img/usdt.svg" />
                        <span class="period">一年</span>
                        <div class="amount">$699</div>
                        <div class="points">赠 2000 积分!</div>
                    </div>
                </div>
        `,
        preConfirm: () => {
            const active = document.querySelector('.pay-card.active');
            if (!active) {
                Swal.showValidationMessage('请选择一种充值方式');
                return false;
            }
            return active.dataset;
        },
        didOpen: () => {
            document.querySelectorAll('.pay-card').forEach(card => {
                card.addEventListener('click', () => {
                    document.querySelectorAll('.pay-card')
                        .forEach(c => c.classList.remove('active'));
                    card.classList.add('active');
                });
            });
        }
    }).then(result => {
        if (result.isConfirmed) {
            Swal.fire({
                icon: 'success',
                title: '充值方式已选择',
                text: `当前方式：${result.value.type.toUpperCase()}`,
                timer: 1200,
                showConfirmButton: false,
                background: '#16213e',
                color: '#e6e6e6',
            });

            // 👉 下一步可进入金额选择 / 支付
            console.log(result.value)
            let request_data = result.value
            request_data["user_id"] = user_id
            $.ajax({
                url: "api/aliyun_pay/",
                method: "POST",
                data: request_data,
                success(res){
                   window.location.href = res.pay_url
                }
            })
        }
    });
}

function getUserDetails(){
    $.ajax({
        url: "api/user_login/",
        method: "GET",
        data: {"user_id": user_id},
        success(res){
           if(res.response_type == "success"){
               is_vip = res.is_vip
               if (user_id && username){
                    updateUserUI(username, res.vip_end_time, res.is_vip)
                    if (is_vip){
                        loadInitialKline()
                        initoldprice()
                        setInterval(UpKline, 1000);
                        setInterval(loadNotifications, 3000);
                    }

                }
           }
        }
    })
}


getUserDetails()

