-- 1.1 Criação das tabelas
CREATE TABLE FILME (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(200) NOT NULL,
    DtCriacao DATETIME NOT NULL,
    Ativo TINYINT NOT NULL,
    GeneroId INT NOT NULL
);

CREATE TABLE GENERO (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(100) NOT NULL,
    DtCriacao DATETIME,
    Ativo TINYINT NOT NULL
);

CREATE TABLE USUARIO (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(200) NOT NULL,
    Email VARCHAR(100),
    CPF VARCHAR(14),
    Ativo TINYINT NOT NULL
);

CREATE TABLE LOCACAO (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    FilmeLocacaoId INT NOT NULL,
    UsuarioId INT NOT NULL,
    DtLocacao DATETIME NOT NULL,
    Ativo TINYINT NOT NULL
);

CREATE TABLE FILMELOCACAO (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    FilmeId INT NOT NULL
);

-- 1.2 Inserção de 20 filmes
INSERT INTO FILME 
VALUES
    (null, 'Filme 1', NOW(), 1, 1),
    (null, 'Filme 2', NOW(), 1, 1),

    -- ...
    (null, 'Filme 20', NOW(), 1, 5);

-- 1.3 Inserção de 5 usuários
INSERT INTO USUARIO
VALUES
    (null, 'Usuário 1', 'usuario1@email.com', '111.111.111-11', 1),
    (null, 'Usuário 2', 'usuario2@email.com', '222.222.222-22', 1),
    (null, 'Usuário 3', 'usuario3@email.com', '333.333.333-33', 1),
    (null, 'Usuário 4', 'usuario4@email.com', '444.444.444-44', 0),
    (null, 'Usuário 5', 'usuario5@email.com', '555.555.555-55', 1);

-- 1.4 Inserção de 5 gêneros
INSERT INTO GENERO 
VALUES
    (NULL, 'Gênero 1', NOW(), 1),
    (NULL, 'Gênero 2', NOW(), 1),
    (NULL, 'Gênero 3', NOW(), 1),
    (NULL, 'Gênero 4', NOW(), 1),
    (NULL, 'Gênero 5', NOW(), 1);

-- 1.5 Inserção de 20 locações
INSERT INTO LOCACAO
VALUES
    (null, 1, 1, NOW(), 1),
    (null, 2, 1, NOW(), 1),
    (null, 3, 1, NOW(), 1),
    (null, 4, 1, NOW(), 1),
    (null, 5, 5, NOW(), 1),
    (null, 6, 2, NOW(), 1),
    (null, 7, 2, NOW(), 1),
    (null, 8, 2, NOW(), 1),
    (null, 9, 5, NOW(), 1),
    (null, 10, 2, NOW(), 1),
    (null, 11, 3, NOW(), 1),
    (null, 12, 3, NOW(), 1),
    (null, 13, 3, NOW(), 1),
    (null, 14, 3, NOW(), 1),
    (null, 15, 5, NOW(), 1),
    (null, 16, 4, NOW(), 1),
    (null, 17, 4, NOW(), 1),
    (null, 18, 4, NOW(), 1),
    (null, 19, 4, NOW(), 1),
    (null, 20, 5, NOW(), 1);


INSERT INTO FILMELOCACAO
VALUES
   (null, 1),
   (null, 2),
   (null, 3),
   (null, 4),
   (null, 5),
   (null, 6),
   (null, 7),
   (null, 8),
   (null, 9),
   (null, 10),
   (null, 11),
   (null, 12),
   (null, 13),
   (null, 14),
   (null, 15),
   (null, 16),
   (null, 17),
   (null, 18),
   (null, 19),
   (null, 20);

-- 1.6 Busca de todas as locações deste mês
SELECT
    F.Nome AS 'Filme.Nome',
    G.Nome AS 'Genero.Nome',
    L.DtLocacao AS 'Locacao.DtLocacao',
    U.Nome AS 'Usuario.Nome',
    U.Email AS 'Usuario.Email'
FROM
    LOCACAO L
JOIN
    FILMELOCACAO FL ON L.FilmeLocacaoId = FL.ID
JOIN
    FILME F ON FL.FilmeId = F.ID
JOIN
    GENERO G ON F.GeneroId = G.ID
JOIN
    USUARIO U ON L.UsuarioId = U.ID
WHERE
    MONTH(L.DtLocacao) = MONTH(NOW());

-- 1.7 Apresentação de todos os usuários inativos que já tiveram alguma locação
SELECT DISTINCT
    U.Nome AS 'Usuario.Nome',
    U.CPF AS 'Usuario.CPF'
FROM
    USUARIO U
JOIN
    LOCACAO L ON U.ID = L.UsuarioId
WHERE
    U.Ativo = 0;

-- 1.8 Apresentação de filmes alugados por usuários que contém a letra “a” em seu email
SELECT
    F.ID AS 'Filme.ID',
    F.Nome AS 'Filme.Nome'
FROM
    FILME F
JOIN
    FILMELOCACAO FL ON F.ID = FL.FilmeId
JOIN
    LOCACAO L ON FL.ID = L.FilmeLocacaoId
JOIN
    USUARIO U ON L.UsuarioId = U.ID
WHERE
    U.Email LIKE '%a%';

-- 1.9 Apresentação dos filmes mais alugados
SELECT
    F.Nome AS 'Filme.Nome',
    COUNT(*) AS 'Quantidade de aluguéis'
FROM
    FILME F
JOIN
    FILMELOCACAO FL ON F.ID = FL.FilmeId
JOIN
    LOCACAO L ON FL.ID = L.FilmeLocacaoId
GROUP BY
    F.Nome
ORDER BY
    COUNT(*) DESC;

