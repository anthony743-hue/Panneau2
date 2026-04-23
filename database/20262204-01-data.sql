-- Insertion groupée des tranches horaires
INSERT INTO TrancheHeure (libelle, heure_debut, heure_fin)
VALUES 
    (N'maraina', '06:00:00', '17:00:00'),
    (N'hariva', '17:00:00', '19:00:00'),
    (N'alina',   '19:00:00', '06:00:00');
GO

INSERT INTO modelePanneau (nom)
VALUES (N'Modele A'), (N'Modele B')
GO;


INSERT INTO ConfigurationPanneauByTranche (id_tranche_heure, pourcentage_ensoleillement, modele_id)
VALUES
    (3, 50.0, 3), -- Alina pour Modele A
    (3, 40.0, 3); -- Alina pour Modele B
    (3, 0, 3)
GO


insert into

INSERT INTO ConfigurationHeurePoint(modele_id, heure_debut, heure_fin,
pourcentage_ouvrable,pourcentage_non_ouvrable) VALUES
(3, '12:00:00', '14:00:00', 50, 0);
(3, '17:00:00', '19:00:00', 50, 40)

INSERT INTO ConfigurationPrixPanneau(modele_id, prix_jour_ouvrable, prix_jour_non_ouvrable)
VALUES
(3, 190,210);