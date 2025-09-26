// Script moderne avec overlay pour gérer les soumissions de formulaires
class FormSubmissionHandler {
    constructor(options = {}) {
        this.config = {
            // Classe CSS de vos boutons de soumission
            buttonClass: options.buttonClass || '.btn',

            // Messages d'attente
            messages: {
                loading: options.loadingMessage || 'Chargement...',
                submitting: options.submittingMessage || 'Envoi en cours...',
                processing: options.processingMessage || 'Traitement...'
            },

            // Sélecteurs
            formSelector: options.formSelector || 'form',

            // Style de l'overlay
            overlay: {
                backgroundColor: options.overlayBg || 'rgba(0, 0, 0, 0.2)',
                zIndex: options.overlayZIndex || 9999,
                spinnerColor: options.spinnerColor || '#ffffff'
            }
        };

        this.activeSubmissions = new Set();
        this.currentOverlay = null;

        this.init();
    }

    init() {
        // Attendre que le DOM soit chargé
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupEventListeners());
        } else {
            this.setupEventListeners();
        }

        this.createOverlayStyles();
    }

    setupEventListeners() {
        // Écouter les soumissions de formulaires
        document.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Écouter les clics sur les boutons/liens
        document.addEventListener('click', (e) => {
            if (e.target.matches(this.config.buttonClass) || e.target.closest(this.config.buttonClass)) {
                this.handleButtonClick(e);
            }
        });

        // Cacher l'overlay quand la page se charge
        window.addEventListener('load', () => this.hideOverlay());

        // Gérer les retours en arrière
        window.addEventListener('pageshow', (e) => {
            this.hideOverlay();
        });
    }

    handleFormSubmit(event) {
        const form = event.target;

        // Vérifier si une soumission est déjà en cours pour ce formulaire
        if (this.activeSubmissions.has(form)) {
            event.preventDefault();
            return false;
        }

        // Marquer la soumission comme active
        this.activeSubmissions.add(form);

        // Afficher l'overlay avec le message de soumission
        this.showOverlay(this.config.messages.submitting);

        return true;
    }

    handleButtonClick(event) {
        const button = event.target.matches(this.config.buttonClass) ?
            event.target :
            event.target.closest(this.config.buttonClass);

        // Si c'est un bouton de type submit, laisser handleFormSubmit s'en occuper
        if (button.type === 'submit') {
            return;
        }

        // Pour les liens et autres boutons
        if (button.tagName === 'a' || button.tagName === 'BUTTON') {
            // Afficher l'overlay
            this.showOverlay(this.config.messages.loading);
        }
    }

    showOverlay(message = 'Chargement...') {
        // Si un overlay existe déjà, le supprimer
        this.hideOverlay();

        // Créer l'overlay
        const overlay = document.createElement('div');
        overlay.className = 'form-submission-overlay';
        overlay.innerHTML = `
            <div class="overlay-content">
                <div class="spinner-container">
                    <div class="modern-spinner"></div>
                </div>
                <div class="overlay-message">${message}</div>
            </div>
        `;

        // Ajouter à la page
        document.body.appendChild(overlay);
        this.currentOverlay = overlay;

        // Animation d'apparition
        requestAnimationFrame(() => {
            overlay.classList.add('visible');
        });

        // Empêcher le scroll
        document.body.style.overflow = 'hidden';
    }

    hideOverlay() {
        if (this.currentOverlay) {
            // Animation de disparition
            this.currentOverlay.classList.remove('visible');

            setTimeout(() => {
                if (this.currentOverlay && this.currentOverlay.parentNode) {
                    this.currentOverlay.parentNode.removeChild(this.currentOverlay);
                }
                this.currentOverlay = null;
            }, 300); // Durée de l'animation
        }

        // Restaurer le scroll
        document.body.style.overflow = '';

        // Nettoyer les soumissions actives
        this.activeSubmissions.clear();
    }

    createOverlayStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .form-submission-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: ${this.config.overlay.backgroundColor};
                z-index: ${this.config.overlay.zIndex};
                display: flex;
                justify-content: center;
                align-items: center;
                opacity: 0;
                transition: opacity 0.3s ease-in-out;
                backdrop-filter: blur(2px);
                -webkit-backdrop-filter: blur(2px);
            }
            
            .form-submission-overlay.visible {
                opacity: 1;
            }
            
            .overlay-content {
                text-align: center;
                color: ${this.config.overlay.spinnerColor};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .spinner-container {
                margin-bottom: 20px;
                display: flex;
                justify-content: center;
            }
            
            .modern-spinner {
                width: 50px;
                height: 50px;
                border: 3px solid rgba(255, 255, 255, 0.7);
                border-top: 3px solid ${this.config.overlay.spinnerColor};
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            .overlay-message {
                font-size: 18px;
                font-weight: 500;
                letter-spacing: 0.5px;
                margin-top: 15px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Animation pulsante pour le message */
            .overlay-message {
                animation: pulse 2s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .modern-spinner {
                    width: 40px;
                    height: 40px;
                }
                
                .overlay-message {
                    font-size: 16px;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Méthodes publiques pour un contrôle manuel
    show(message = null) {
        this.showOverlay(message || this.config.messages.loading);
    }

    hide() {
        this.hideOverlay();
    }

    isVisible() {
        return this.currentOverlay !== null;
    }
}

// Initialisation automatique
let formHandler;

// Fonction d'initialisation
function initFormSubmissionHandler(options = {}) {
    formHandler = new FormSubmissionHandler(options);
    return formHandler;
}

// Auto-initialisation avec configuration par défaut
document.addEventListener('DOMContentLoaded', () => {
    if (!window.formSubmissionHandler) {
        window.formSubmissionHandler = initFormSubmissionHandler();
    }
});

// Exposer globalement pour un usage manuel
window.FormSubmissionHandler = FormSubmissionHandler;
window.initFormSubmissionHandler = initFormSubmissionHandler;
// // Script pour gérer les soumissions de formulaires et éviter les clics multiples
