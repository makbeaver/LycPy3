function del_item(e) {
    item_id = event.path[0].id.slice(9)
    console.log(`Deleting item #${item_id}`)
    let xhr = new XMLHttpRequest()
    xhr.open("GET", `/api/del_item/${item_id}`, true)
    xhr.send(null)
    console.log(xhr.responseText)

    e.path[3].remove() // Delete card
}

function buy_item(e) {
    console.log(event)
    item_id = event.path[0].id.slice(9)
    console.log(`Buy item #${item_id}`)
    let xhr = new XMLHttpRequest()
    xhr.open("GET", `/api/buy_item/${item_id}`, true)
    xhr.send(null)
    console.log(xhr.responseText)
    e.path[0].firstElementChild.innerHTML = +e.path[0].firstElementChild.innerHTML + 1
}

function del_item_cart(e)
{
    console.log(event)
    item_id = event.path[0].id.slice(14)
    console.log(`Del item from cart #${item_id}`)
    let xhr = new XMLHttpRequest()
    xhr.open("GET", `/api/del_item_cart/${item_id}`, true)
    xhr.send(null)
    console.log(xhr.responseText)
    if (+e.path[0].previousElementSibling.firstElementChild.innerHTML > 0)
    {
        e.path[0].previousElementSibling.firstElementChild.innerHTML = +e.path[0].previousElementSibling.firstElementChild.innerHTML - 1
    }
}

function home(e)
{
    console.log(event)

}