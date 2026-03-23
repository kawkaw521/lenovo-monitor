import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────
# CONFIGURATION — modifie ces valeurs
# ─────────────────────────────────────────────
TARGET_KEYWORDS = [
    "legion pro 7i",
    "rtx 5090",
    "10e génération",
    "10th gen",
    "16 pouces",
    "16\""
]

LENOVO_SEARCH_URL = "https://www.lenovo.com/ca/fr/c/laptops/legion/?visibleDatas=812%3AIntel%C2%AE+Core%E2%84%A2+Ultra+9%3B541%3ARTX+5090"

# Ces valeurs viennent des secrets GitHub (ne pas mettre ici en clair)
OUTLOOK_EMAIL = os.environ.get("OUTLOOK_EMAIL")      # ton courriel Outlook
OUTLOOK_PASSWORD = os.environ.get("OUTLOOK_PASSWORD") # mot de passe app Outlook
TO_EMAIL = os.environ.get("TO_EMAIL")                 # destinataire (peut être toi-même)

# ─────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────

def check_availability():
    """Vérifie si le Legion Pro 7i RTX 5090 est disponible sur Lenovo Canada."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    products_found = []

    try:
        response = requests.get(LENOVO_SEARCH_URL, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Cherche les cartes de produits
        product_cards = soup.find_all(
            ["div", "li", "article"],
            class_=lambda c: c and any(
                kw in c.lower() for kw in ["product", "item", "card", "tile"]
            )
        )

        for card in product_cards:
            card_text = card.get_text(separator=" ").lower()

            # Vérifie que le produit correspond aux mots-clés
            matches = sum(1 for kw in TARGET_KEYWORDS if kw.lower() in card_text)

            if matches >= 2:  # au moins 2 mots-clés présents
                # Cherche le titre et le lien
                title_el = card.find(["h2", "h3", "h4", "a"])
                title = title_el.get_text(strip=True) if title_el else "Legion Pro 7i"

                link_el = card.find("a", href=True)
                link = link_el["href"] if link_el else LENOVO_SEARCH_URL
                if link.startswith("/"):
                    link = "https://www.lenovo.com" + link

                # Cherche le prix
                price_el = card.find(
                    class_=lambda c: c and "price" in c.lower()
                )
                price = price_el.get_text(strip=True) if price_el else "Prix non affiché"

                # Vérifie disponibilité (bouton "Ajouter au panier" ou "Acheter")
                btn = card.find(
                    ["button", "a"],
                    string=lambda s: s and any(
                        w in s.lower() for w in ["panier", "acheter", "add to cart", "buy"]
                    )
                )
                available = btn is not None

                if available:
                    products_found.append({
                        "title": title,
                        "price": price,
                        "link": link
                    })

        print(f"✅ {len(products_found)} produit(s) disponible(s) trouvé(s).")
        return products_found

    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
        return []


def send_email(products):
    """Envoie un courriel Outlook avec les produits trouvés."""
    if not products:
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🎮 Legion Pro 7i RTX 5090 — {len(products)} produit(s) disponible(s) !"
    msg["From"] = OUTLOOK_EMAIL
    msg["To"] = TO_EMAIL

    # Corps du courriel en HTML
    items_html = ""
    for p in products:
        items_html += f"""
        <div style="border:1px solid #ddd; border-radius:8px; padding:16px; margin:12px 0;">
            <h3 style="margin:0 0 8px 0; color:#e8001a;">{p['title']}</h3>
            <p style="margin:4px 0;"><strong>Prix :</strong> {p['price']}</p>
            <a href="{p['link']}" style="
                display:inline-block; margin-top:10px;
                background:#e8001a; color:white;
                padding:8px 18px; border-radius:4px;
                text-decoration:none; font-weight:bold;
            ">Voir le produit →</a>
        </div>
        """

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif; max-width:600px; margin:auto;">
        <h2 style="color:#e8001a;">🎮 Lenovo Legion Pro 7i disponible !</h2>
        <p>Le modèle que tu surveilles vient d'apparaître sur le site Lenovo Canada :</p>
        {items_html}
        <hr style="margin-top:24px;">
        <p style="font-size:12px; color:#888;">
            Alerte générée automatiquement — Lenovo Legion Monitor
        </p>
    </body></html>
    """

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
            server.starttls()
            server.login(OUTLOOK_EMAIL, OUTLOOK_PASSWORD)
            server.sendmail(OUTLOOK_EMAIL, TO_EMAIL, msg.as_string())
        print(f"📧 Courriel envoyé à {TO_EMAIL} !")
    except Exception as e:
        print(f"❌ Erreur envoi courriel : {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🔍 Vérification de la disponibilité du Legion Pro 7i RTX 5090...")
    available_products = check_availability()

    if available_products:
        print(f"🎯 Produit(s) trouvé(s) ! Envoi du courriel...")
        send_email(available_products)
    else:
        print("😴 Pas encore disponible. On réessaiera bientôt.")
