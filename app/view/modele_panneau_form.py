from app.controller.modele_panneau_form_controller import (
    ModelePanneauFormController,
)
from app.utils import get_default_tranches, get_modele_panneau_payloads
from app.view.modele_panneau_form_view import ModelePanneauFormView


class ModelePanneauForm(ModelePanneauFormView):
    def __init__(self, master=None, modeles_store=None):
        self.modeles_store = (
            modeles_store
            if modeles_store is not None
            else get_modele_panneau_payloads()
        )
        self.tranches = get_default_tranches()
        super().__init__(master=master, tranches=self.tranches)
        self.controller = ModelePanneauFormController(
            modeles_store=self.modeles_store,
            tranches=self.tranches,
            view=self,
        )


def open_modele_panneau_form(master=None, modeles_store=None):
    return ModelePanneauForm(master=master, modeles_store=modeles_store)
