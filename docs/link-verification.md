# Official link verification

Checked on 2026-11-19. Scope: all 20 unique government and electoral-authority URLs found in the service catalog, frontend, and design references. Repository-wide URL search found no additional government links.

Method: HTTP GET requests with redirects, response titles, and official search results for replacement addresses. This checks link availability and destination identity; it does not certify every statement in the draft service records. Keep `source.reviewedAt` null until the team completes the content review.

## Changes

- Fixed five HTTP 404 destinations: national identity card (CIN), salary bonus, BPC, CRAS, and ID Jovem. The BPC and CRAS paths require uppercase `SUAS`.
- Replaced the CAIXA FGTS destination, which produced a redirect loop in the automated request, with the accessible GOV.BR service page. That page includes balance consultation and official service channels. This was not classified as a 404.
- Replaced the passport redirect with its current destination.
- Kept the TSE auto-service address: official electoral-authority pages still reference it. Direct automated access returned HTTP 403, so successful access could not be confirmed.

## Results

All 19 GOV.BR destinations returned HTTP 200. The TSE destination returned HTTP 403. Availability is a snapshot, not a guarantee of future access. Design System routes share a JavaScript application shell; HTTP 200 alone does not verify every rendered component.

| Reference | Destination | GET result |
| --- | --- | --- |
| Padrão Digital de Governo - Design System | [Official page](https://www.gov.br/ds/) | 200 |
| Padrão Digital de Governo - Design System | [Official page](https://www.gov.br/ds/fundamentos-visuais/tipografia) | 200 |
| Padrão Digital de Governo - Design System | [Official page](https://www.gov.br/ds/templates/base) | 200 |
| Manual de Diretrizes GOV.BR | [Official page](https://www.gov.br/gestaodeconteudo/pt-br/manuais-e-tutoriais/diretrizes-para-edicao-de-conteudo/manual-de-diretrizes-gov.br) | 200 |
| identity | [Official page](https://www.gov.br/governodigital/pt-br/identidade/cin) | 200 |
| bpc | [Official page](https://www.gov.br/mds/pt-br/acoes-e-programas/SUAS/beneficios-assistenciais/beneficio-assistencial-ao-idoso-e-a-pessoa-com-deficiencia-bpc) | 200 |
| cras | [Official page](https://www.gov.br/mds/pt-br/acoes-e-programas/SUAS/unidades-de-atendimento/centro-de-referencia-de-assistencia-social-cras) | 200 |
| family-benefit | [Official page](https://www.gov.br/mds/pt-br/acoes-e-programas/bolsa-familia) | 200 |
| GOV.BR | [Official page](https://www.gov.br/pt-br) | 200 |
| cpf | [Official page](https://www.gov.br/pt-br/servicos/inscrever-no-cpf) | 200 |
| social-registry | [Official page](https://www.gov.br/pt-br/servicos/inscrever-se-no-cadastro-unico-para-programas-sociais-do-governo-federal) | 200 |
| youth-id | [Official page](https://www.gov.br/pt-br/servicos/obter-a-carteira-de-identidade-jovem) | 200 |
| work-card | [Official page](https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho) | 200 |
| passport | [Official page](https://www.gov.br/pt-br/servicos/obter-passaporte-comum-para-brasileiro) | 200 |
| salary-bonus | [Official page](https://www.gov.br/pt-br/servicos/receber-o-abono-salarial) | 200 |
| fgts | [Official page](https://www.gov.br/pt-br/servicos/sacar-o-fgts) | 200 |
| unemployment | [Official page](https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego) | 200 |
| cpf-status | [Official page](https://www.gov.br/receitafederal/pt-br/assuntos/meu-cpf) | 200 |
| jobs | [Official page](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/sistema-nacional-de-emprego-sine) | 200 |
| voter | [Official page](https://www.tse.jus.br/servicos-eleitorais/autoatendimento-eleitoral) | 403; automated access blocked |

The portal guidelines page returned its expected title and document content; error-page wording embedded in the HTML must not be interpreted as the page itself returning 404.
