#!/bin/bash
npx staticrypt "$1" -p "$2" \
	--short \
	--template ./template.html \
	--template-button "Déchiffrer" \
	--template-color-primary "#052851" \
	--template-color-secondary "#374f6b" \
	--template-instructions "Veuillez vous référer à vos supérieurs si vous n'avez pas l'accès" \
	--template-error "Mauvais mot de passe" \
	--template-placeholder "Mot de passe" \
	--template-title "CONFIDENTIEL" \
	--template-remember "Se souvenir" \
	--template-toggle-hide "Cacher le mot de passe" \
	--template-toggle-show "Montrer le mot de passe"
