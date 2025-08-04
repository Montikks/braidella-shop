from django import forms
import re

ZIP_RE = re.compile(r"^\d{3}\s?\d{2}$")
PHONE_RE = re.compile(r"^\+?[\d\s]{9,15}$")

DELIVERY_CHOICES = [
    ("address", "Doručení na adresu"),
    ("balikovna", "Balíkovna (výdejní místo)"),
]

class AddressForm(forms.Form):
    # povinné
    first_name = forms.CharField(label="Jméno", max_length=60)
    last_name = forms.CharField(label="Příjmení", max_length=60)
    email = forms.EmailField(label="E-mail", max_length=120)
    phone = forms.CharField(label="Telefon", max_length=20, help_text="Např. +420 123 456 789")

    # doprava
    delivery_method = forms.ChoiceField(
        label="Způsob doručení",
        choices=DELIVERY_CHOICES,
        widget=forms.RadioSelect
    )

    # adresa – budou povinné jen když je zvolena „address“
    street = forms.CharField(label="Ulice a č.p.", max_length=120, required=False)
    city = forms.CharField(label="Město", max_length=80, required=False)
    zip_code = forms.CharField(label="PSČ", max_length=10, required=False, help_text="Např. 110 00")

    # Balíkovna – povinné jen když je zvolena „balikovna“
    balikovna_id = forms.CharField(
        label="Výdejní místo Balíkovny (ID/adresa)",
        max_length=160,
        required=False,
        help_text="Vyberete v dalším kroku z mapy, nebo zadejte ručně."
    )

    def clean_zip_code(self):
        z = (self.cleaned_data.get("zip_code") or "").strip()
        if not z:
            return z
        if not ZIP_RE.match(z):
            raise forms.ValidationError("Zadej PSČ ve tvaru 110 00.")
        return z

    def clean_phone(self):
        p = (self.cleaned_data.get("phone") or "").strip()
        if not PHONE_RE.match(p):
            raise forms.ValidationError("Zadej platné telefonní číslo (může být s +420).")
        return p

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get("delivery_method")
        if method == "address":
            # vyžaduj adresní pole
            for f in ("street", "city", "zip_code"):
                if not (cleaned.get(f) or "").strip():
                    self.add_error(f, "Toto pole je povinné pro doručení na adresu.")
            # Balíkovnu vynuluj
            cleaned["balikovna_id"] = ""
        elif method == "balikovna":
            if not (cleaned.get("balikovna_id") or "").strip():
                self.add_error("balikovna_id", "Vyberte nebo zadejte Balíkovnu.")
            # Adresu klidně ponecháme prázdnou
        return cleaned
