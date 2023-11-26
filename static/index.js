function game(keyValue) 
{
    const board = document.getElementById('board');
    const color_board = document.getElementById('color_board');
    

    const keyData = 
    {
        board: board.value,  
        color_board: color_board.value,
        key: keyValue,
    };


    fetch('/game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(keyData)
    })
    .then(response => response.json())
    .then(data => {
        if (data['success'] === true) 
        {
            board_receive = data['board'];
            color_board_receive = data['color'];
            board.value = JSON.stringify(board_receive);
            color_board.value = JSON.stringify(color_board_receive);

            if (data['category'] === 'special')
            {
                if (data['value'] === 'DELETE')
                {
                    const cell = document.getElementById(`${data['position']}`);
                    cell.innerHTML = '';
                }

                else if (data['value'] === 'ENTER')
                {
                    if (data['isDone'] === true)
                    {
                        showAndHideAlertWithRedirect(data['message'], 5000);
                    }

                    else if (data['inlist'] === true)
                    {
                        for (let j = 0; j < data['color'][data['position']].length; j++)
                        {
                            let box = document.getElementById(`${data['position']}_${j}`);
                            if (data['color'][data['position']][j] === 'GREEN')
                            {
                                box.style.backgroundColor = "#528d4e";
                            }
                            else if (data['color'][data['position']][j]  === 'YELLOW')
                            {
                                box.style.backgroundColor = "#b49f39";
                            }
                            else
                            {
                                box.style.backgroundColor = "#ea433b";
                            }
                        }
                    }

                    else if (data['inlist'] === false)
                    {
                        showAndHideAlert(data['message'], 2000);
                    }

                    else if (data['notEnough'] === true)
                    {
                        showAndHideAlert(data['message'], 2000);
                    }
                }
            }
            else if (data['category'] === 'notspecial')
            {
                const cell = document.getElementById(`${data['position']}`);
                cell.innerHTML = data['value'];
            }
        }
    });
}

function showAndHideAlert(message, timeout) 
{
    const alertElement = document.getElementById("alert");
    alertElement.textContent = message;
    alertElement.style.display = "block";


    setTimeout(function () 
    {
        alertElement.style.display = "none";
    }, timeout);
    
}

function showAndHideAlertWithRedirect(message, timeout) 
{
    const alertElement = document.getElementById("alert");
    alertElement.textContent = message;
    alertElement.style.display = "block";


    setTimeout(function () 
    {
        alertElement.style.display = "none";
        window.location.href = "/gameover";
    }, timeout);
    
}