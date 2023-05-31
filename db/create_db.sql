DROP VIEW IF EXISTS TagByGroup;
DROP VIEW IF EXISTS HostHasTagView;

DROP TABLE IF EXISTS HostHasTag;
DROP TABLE IF EXISTS Host;
DROP TABLE IF EXISTS Tag;
DROP TABLE IF EXISTS Metadata;

CREATE TABLE Host (
	HostID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	Hostname VARCHAR(255) NOT NULL UNIQUE,
	CommissionDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	DecommissionDate TIMESTAMP NULL,
	Description TEXT,
	Variables JSON NOT NULL DEFAULT ("{}")
);

CREATE TABLE Tag (
	TagID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	TagName VARCHAR(64) NOT NULL UNIQUE,
	TagGroup VARCHAR(64),
	Description TEXT,
	Variables JSON NOT NULL DEFAULT ("{}")
);

CREATE TABLE HostHasTag (
	HostID INT NOT NULL,
	TagID INT NOT NULL,
	PRIMARY KEY (HostID, TagID),
	CONSTRAINT FK_HostHasTagHost FOREIGN KEY (HostID)
		REFERENCES Host(HostID),
	CONSTRAINT FK_HostHasTagTag FOREIGN KEY (TagID)
		REFERENCES Tag(TagID)
);

CREATE TABLE Metadata (
	KeyName VARCHAR(64) NOT NULL PRIMARY KEY,
	Value TEXT
);

INSERT INTO Tag (TagName, Description) VALUES
	('all',		'Special tag that applies to all hosts. The host list is ignored for this tag; it will always apply to every host in Isidore.'),
	('ungrouped',	'Special tag that applies to hosts that do not have a tag. In addition to any hosts assigned to this tag, it will always apply to every host that does not have a tag.');

INSERT INTO Metadata (KeyName, Value) VALUES
	('version', '0.1.6-dev0')
;

CREATE VIEW HostHasTagView AS
	SELECT
		Host.HostID,
		Host.Hostname,
		Tag.TagID,
		Tag.TagName
	FROM Host
	INNER JOIN HostHasTag
		ON Host.HostID = HostHasTag.HostID
	LEFT JOIN Tag
		ON HostHasTag.TagID = Tag.TagID
	WHERE Host.DecommissionDate IS NULL;

CREATE VIEW TagByGroup AS
	SELECT
		TagGroup,
		GROUP_CONCAT(
			TagName
			ORDER BY TagName
			SEPARATOR ', ')
		AS 'Tags'
	FROM Tag
	GROUP BY TagGroup
	ORDER BY TagGroup;

