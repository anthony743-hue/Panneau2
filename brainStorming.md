# Formalisation générale du système photovoltaïque

## 1. Périodes solaires et puissance disponible

On divise la journée en trois intervalles avec des puissances relatives fixes.

### 1.1. Matinée (06h → 17h)

**Durée :** 11 heures

**Puissance solaire fournie :**
$$P_{\text{matin}} = 0.40 \, S$$

où $S$ est la puissance nominale totale du panneau.

### 1.2. Après-midi (17h → 19h)

**Durée :** 2 heures

**Puissance disponible :**
$$P_{\text{aprem}} = 0.20 \, S = \frac{1}{2} P_{\text{matin}}$$

### 1.3. Soir / Nuit (19h → 06h)

$$P_{\text{nuit}} = 0$$

## 2. Charge de la batterie

On pose :
- $x$ = énergie fournie par le panneau chaque heure le matin
- $y$ = énergie fournie chaque heure l'après-midi

### Équation globale

La batterie doit être chargée entièrement :
$$11x + 2y = \text{Charge}$$

### Relation matin ↔ après-midi

$$y = \frac{x}{2}$$

### Substitution

$$11x + 2\left(\frac{x}{2}\right) = 11x + x = 12x$$

Donc :
$$x = \frac{\text{Charge}}{12}$$
$$y = \frac{\text{Charge}}{24}$$

## 3. Puissance des appareils

Plusieurs appareils peuvent fonctionner simultanément.

**Puissance instantanée :**
$$P(t) = \sum_{i \in A(t)} P_i$$

**Puissance maximale à couvrir :**
$$P_{\max} = \max_t P(t)$$

## 4. Panneau = Appareils + Recharge batterie

### 4.1. Matinée

$$P_{\text{matin}} = x + P_{\text{jour}}$$

### 4.2. Après-midi

$$P_{\text{aprem}} = y + P_{\text{aprem,max}}$$

### 4.3. Contrainte solaire imposée

$$x + P_{\text{jour}} = 2\left(y + P_{\text{aprem,max}}\right)$$

Avec $y = x/2$ :
$$x + P_{\text{jour}} = x + 2 \, P_{\text{aprem,max}}$$

### 4.4. Consolidation avec la charge

**Puissance nominale requise :**
$$S = \frac{2}{3}\left(12x + P_{\text{jour}} + P_{\text{aprem,max}}\right)$$

Or $x = \frac{\text{Charge}}{12}$, donc :

$$\boxed{S = \frac{2}{3}\left(\text{Charge} + P_{\text{jour}} + P_{\text{aprem,max}}\right)}$$

## 5. Structuration des appareils

Chaque appareil possède :
- une puissance $P_i$
- une plage horaire $[h_{\text{début}}, h_{\text{fin}}]$

On les convertit en heures entières pour calculer :
- $P_{\text{jour}}$
- $P_{\text{aprem,max}}$
- $P_{\max}$

## 6. Batterie : marge de sécurité

$$\text{Charge}_{\text{réelle}} = 1.5 \times \text{Charge}$$

---

✔️ Formatage Markdown 100% complet.