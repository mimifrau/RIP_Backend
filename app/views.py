from django.shortcuts import render

codes = [
    {
        "id": 1,
        "name": "1010",
        "description": "Дивиденды — это часть прибыли, которой компания делится с инвесторами, владеющими их акциями. Некоторые компании выплачивают дивиденды от 1 до 12 раз в год — периодичность и размер выплат указываются в дивидендной политике конкретной компании.",
        "decryption": "Дивиденды",
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "1220",
        "description": "Под страховыми взносами понимаются обязательные платежи на обязательное пенсионное страхование, обязательное социальное страхование на случай временной нетрудоспособности и в связи с материнством, на обязательное медицинское страхование.",
        "decryption": "Суммы страховых взносов",
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "1537",
        "description": "Процент по займу – это сумма, которую клиент платит за пользование средствами, полученными в долг.",
        "decryption": "Доходы в виде процентов по займу",
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "1549",
        "description": "Ценная бумага — это финансовое средство, дающее заимодавцу (инвестору) обеспеченное законом право получать в будущем определенный доход в установленном порядке.",
        "decryption": "Доходы, полученные по операциям с ценными бумагами",
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "2014",
        "description": "По правилам Трудового кодекса, в случае увольнения работодатель должен компенсировать сотруднику временную потерю заработка.",
        "decryption": "Сумма выплаты в виде выходного пособия",
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "2017",
        "description": "Полевое довольствие – это компенсационная выплата, которая связана с разъездным характером работы или работой в полевых условиях.",
        "decryption": "Суточные или полевое довольствие работникам",
        "image": "http://localhost:9000/images/6.png"
    }
]

draft_tax = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "period": "24 августа 2024г - 24 сентября 2024г",
    "codes": [
        {
            "id": 1,
            "value": 1200
        },
        {
            "id": 2,
            "value": 2500
        },
        {
            "id": 3,
            "value": 3000
        }
    ]
}


def getCodeById(code_id):
    for code in codes:
        if code["id"] == code_id:
            return code


def getCodes():
    return codes


def searchCodes(code_name):
    res = []

    for code in codes:
        if code_name.lower() in code["name"].lower():
            res.append(code)

    return res


def getDraftTax():
    return draft_tax


def getTaxById(tax_id):
    return draft_tax


def index(request):
    code_name = request.GET.get("code_name", "")
    codes = searchCodes(code_name) if code_name else getCodes()
    draft_tax = getDraftTax()

    context = {
        "codes": codes,
        "code_name": code_name,
        "codes_count": len(draft_tax["codes"]),
        "draft_tax": draft_tax
    }

    return render(request, "home_page.html", context)


def code(request, code_id):
    context = {
        "id": code_id,
        "code": getCodeById(code_id),
    }

    return render(request, "code_page.html", context)


def tax(request, tax_id):
    tax = getTaxById(tax_id)
    codes = [
        {**getCodeById(code["id"]), "value": code["value"]}
        for code in tax["codes"]
    ]

    context = {
        "tax": tax,
        "codes": codes
    }

    return render(request, "tax_page.html", context)
