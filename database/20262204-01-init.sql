IF DB_ID(N'PanneauSolaireDB') IS NULL
BEGIN
    CREATE DATABASE PanneauSolaireDB;
END
GO

CREATE TABLE modelePanneau (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nom NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE TrancheHeure (
    id INT IDENTITY(1,1) PRIMARY KEY,
    libelle NVARCHAR(120) NOT NULL,
    heure_debut TIME(0) NOT NULL,
    heure_fin TIME(0) NOT NULL
);
GO

CREATE TABLE ConfigurationPanneauByTranche(
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_tranche_heure INT NOT NULL,
    pourcentage_ensoleillement FLOAT NOT NULL,
    FOREIGN KEY (id_tranche_heure) REFERENCES TrancheHeure(id)
);
GO

ALTER TABLE ConfigurationPanneauByTranche ADD modele_id INT NOT NULL;

ALTER TABLE ConfigurationPanneauByTranche ADD CONSTRAINT Fk_Configuration_Modele 
FOREIGN KEY (modele_id) REFERENCES modelePanneau(id);

CREATE TABLE ConfigurationPrixPanneau(
    id INT IDENTITY(1,1) PRIMARY KEY,
    modele_id INT NOT NULL,
    prix_jour_ouvrable INT DEFAULT 0,
    prix_jour_non_ouvrable INT DEFAULT 0,
    FOREIGN KEY (modele_id) REFERENCES modelePanneau(id)
);
GO

CREATE TABLE ConfigurationHeurePoint(
    id INT IDENTITY(1,1) PRIMARY KEY,
    modele_id INT NOT NULL,
    heure_debut TIME(0) NOT NULL,
    heure_fin TIME(0) NOT NULL,
    pourcentage_ouvrable INT NOT NULL DEFAULT 0,
    pourcentage_non_ouvrable iNT NOT NULL DEFAULT 0,
    FOREIGN KEY (modele_id) REFERENCES  modelePanneau(id)
);
GO

DELETE FROM ConfigurationHeurePoint;

DELETE FROM ConfigurationPanneauByTranche WHERE modele_id = 3