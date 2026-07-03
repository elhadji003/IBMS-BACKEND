import paydunya
from paydunya import InvoiceItem, Store
from django.conf import settings


def create_paydunya_invoice(payment):
    # 1. Configuration GLOBALE
    paydunya.debug = (settings.PAYDUNYA_MODE == "live")
    paydunya.api_keys = {
        "PAYDUNYA-MASTER-KEY": settings.PAYDUNYA_MASTER_KEY,
        "PAYDUNYA-PRIVATE-KEY": settings.PAYDUNYA_PRIVATE_KEY,
        "PAYDUNYA-PUBLIC-KEY": settings.PAYDUNYA_PUBLIC_KEY,
        "PAYDUNYA-TOKEN": settings.PAYDUNYA_TOKEN,
    }
    paydunya.setup_mode = settings.PAYDUNYA_MODE

    # 2. Boutique & Redirections
    store = Store(name="LearnTech")
    frontend_base_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    
    store.return_url = f"{frontend_base_url}/payment/success"
    store.cancel_url = f"{frontend_base_url}/payment/cancel"

    # 3. Articles
    items = [
        InvoiceItem(
            name=payment.course.title,
            quantity=1,
            unit_price=f"{payment.amount:.2f}",
            total_price=f"{payment.amount:.2f}",
            description=f"Accès au cours : {payment.course.title}"
        )
    ]

    # 4. Facture via l'API standard Invoice
    invoice = paydunya.Invoice(store)
    invoice.add_items(items)
    invoice.add_custom_data([("payment_id", str(payment.id))])
    
    # 🎯 FORCE L'AFFICHAGE DE TOUS LES MOYENS DE PAIEMENT LOCAUX COCHÉS (Wave, OM, Free Money)
    invoice.add_channels(['all'])

    # 5. Envoi
    success, response = invoice.create()

    if success:
        token = response.get("token")
        
        if not token:
            return {
                "success": False,
                "error": f"Paiement accepté mais aucun token reçu. Réponse : {response}"
            }
            
        # 🎯 LES VRAIES URLS OFFICIELLES SANS SOUS-DOMAINE BLOQUANT
        if settings.PAYDUNYA_MODE == "test":
            url_paiement = f"https://paydunya.com/sandbox-checkout/invoice/{token}"
        else:
            url_paiement = f"https://paydunya.com/checkout/invoice/{token}"

        return {
            "success": True,
            "token": token,
            "url": url_paiement
        }

    return {
        "success": False,
        "error": response
    }