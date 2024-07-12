# Connecteur Azure Storage
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE.md)&nbsp;
[![fr](https://img.shields.io/badge/lang-en-red.svg)](README.md)

Cette intégration permet d'interagir avec Azure Blob Storage à partir des Traitement ou Ressources Visual TOM.
Plusieurs interactions sont disponibles :
    * Téléchargement
    * Téléversement
    * Liste (pour vérifier si un fichier est présent)

# Avertissement
Aucun support ni garanties ne seront fournis par Absyss SAS pour ce projet et les fichiers associés. L'utilisation est à vos propres risques.

Absyss SAS ne peut être tenu responsable des dommages causés par l'utilisation d'un des fichiers mis à disposition dans ce dépôt Github.

Il est possible de faire appel à des jours de consulting pour l'implémentation.

# Prérequis

  * Visual TOM 7.1 ou plus récent
  * Python 3.x installé sur l'agent
  * Compte Azure Storage avec un stockage Blob existant
  * Installation des packages Python nécessaires via la commande :
    ```bash
    pip install -r requirements.txt
    ```
  * Agent Unix (l'utilisation sous Windows sera disponible plus tard)

# Consignes

  * Créer une application Azure et définir les variables d'environnement suivantes dans le fichier config.py dans le même répertoire (un modèle de fichier est présent dans le dépôt) :
    * `AZURE_CLIENT_ID`: ID de l'application Azure
    * `AZURE_TENANT_ID`: ID de l'annuaire
    * `AZURE_CLIENT_SECRET`: Secret de l'application
    * `AZURE_STORAGE_NAME`: Nom du compte de stockage Azure
  * Créer dans Visual TOM, une connexion "Applicatifs personnalisés" avec la définition suivante :
    ![Capture Applicatif Personnalisé](screenshots/Azure_Storage_CustomApplication.png?raw=true)

Lorsque l'utilisation est dans un Traitement, 2 actions sont disponibles :
  * Télécharger un fichier depuis le conteneur de stockage Azure vers un répertoire local
  * Téléverser un fichier depuis un répertoire local vers un conteneur de stockage Azure

Lorsque l'utilisation est dans une Ressource générique :
  * Lister pour vérifier l'existence de fichiers dans le conteneur

Description des paramètres (sensible à la casse) :
    * `Container name` : Nom du conteneur de stockage
    * `Type of transfer` : Download, Upload ou List (Téléchargement, Téléversement ou Liste)
    * `Local path` : Dossier (chemin absolu) où se trouve le fichier ou où il sera téléchargé. Requis pour le Téléchargement et le Téléversement.
    * `Remote path` : Optionnel. Chemin où se trouve le fichier dans le conteneur ou où il sera stocké.
    * `Filename` : Nom du ou des fichiers à gérer. Cette valeur accepte des expressions régulières de type "Unix"
    * `Overwrite` : Spécifie ce qui se passe si un fichier est déjà présent à la destination (par défaut : Écraser)
    * `Error if no file found` : Spécifie ce qui se passe s'il n'y a aucun fichier à Téléverser/Télécharger (par défaut : Erreur)

Lorsqu'il est utilisé dans la Ressource générique, la définition est :
    * `Batch queue` : queue_azstorage
    * `Script` : #
    * `Paramètre #1` : Nom du conteneur
    * `Paramètre #2` : Liste
    * `Paramètre #3` : Chemin distant (optionnel)
    * `Paramètre #4` : Nom du fichier (peut inclure des expressions régulières de type "Unix")

L'intégration renvoie des codes spécifiques pour les erreurs :
    * 90 : Paramètres incohérents
    * 91 : Aucun fichier trouvé et "Erreur si aucun fichier trouvé" activé ou Type de transfert = Liste
    * 92 : Au moins 1 fichier n'a pas été transféré en raison de la présence d'un fichier existant et "Écraser" désactivé
    * 99 : Exception inconnue capturée par le script

# Licence
Ce projet est sous licence Apache 2.0. Voir le fichier [LICENCE](license) pour plus de détails.


# Code de conduite
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.1%20adopted-ff69b4.svg)](code-of-conduct.md)  
Absyss SAS a adopté le [Contributor Covenant](CODE_OF_CONDUCT.md) en tant que Code de Conduite et s'attend à ce que les participants au projet y adhère également. Merci de lire [document complet](CODE_OF_CONDUCT.md) pour comprendre les actions qui seront ou ne seront pas tolérées.
