# GatoVSRatonIAproyect
Owner Yohan Michel Perez Monzon Ing Informatica 3er año

Descripción del Problema 

El problema central de este proyecto consiste en desarrollar un sistema de inteligencia artificial donde un ratón aprende a escapar de un gato en un laberinto generado aleatoriamente. En este escenario, el ratón debe navegar por el entorno mientras busca comida para mantener su energía, generando olor que el gato puede seguir. La clasificación tradicional de comportamientos de escape en entornos laberínticos depende de estrategias predefinidas o reglas heurísticas, pero este enfoque presenta limitaciones en términos de adaptabilidad y eficiencia. 

La transición hacia un enfoque basado en aprendizaje por refuerzo representa un avance significativo hacia métodos más dinámicos y adaptables. Este modelo tiene aplicaciones prácticas en la simulación de comportamientos de evasión, optimización de rutas en entornos complejos, y el estudio de estrategias de persecución-escape en sistemas biológicos y artificiales. El desafío técnico radica en desarrollar un agente capaz de tomar decisiones óptimas en tiempo real, equilibrando la búsqueda de recursos, la gestión de energía, y la evasión de amenazas. 
Entorno del Juego 

El entorno del juego es un laberinto procedural generado aleatoriamente con: 

     Pasillos interconectados y obstáculos fijos
     Distribución dinámica de comida dispersa por el mapa
     Sistema de detección sensorial basado en olor
     

Características Principales 

     Tipo de problema: Aprendizaje por refuerzo en entorno parcialmente observable
     Número de agentes: 2 (ratón y gato)
     Elementos ambientales: Comida, paredes, puntos de escape
     Sistema de percepción: Detección de olor con intensidad decreciente según distancia y tiempo
     Dinámica de energía: Consumo constante durante movimiento, restauración mediante comida
     

Elementos del Juego 

Ratón (Agente Principal): 

     Estado: Posición en el laberinto, nivel de energía
     Comportamiento: Navegación, búsqueda de comida, evasión estratégica
     Interacción: Genera olor al consumir comida, consume energía durante movimiento
     

Gato (Agente Adversario): 

     Estado: Posición en el laberinto, memoria de rastreo
     Comportamiento: Persecución basada en detección olfativa
     Interacción: Sigue el rastro de olor generado por el ratón
     

Comida: 

     Dispersa aleatoriamente en el laberinto
     Proporciona energía al ratón cuando es consumida
     No genera olor por sí misma
     

Olor: 

     Generado únicamente cuando el ratón consume comida
     Dispersión gradual en el entorno con intensidad decreciente
     Detectable por el gato como pista de seguimiento
     

Contexto del Problema y Selección Algorítmica 

Para abordar este problema, se recomienda la implementación de algoritmos de aprendizaje por refuerzo que han demostrado excelente rendimiento en problemas de toma de decisiones secuenciales con percepción sensorial: Q-Learning y SARSA. Esta selección se fundamenta en sus características técnicas y adecuación al dominio específico del problema. 

Q-Learning - Enfoque Basado en Valores de Estado-Acción
Fundamentación Teórica 

Q-Learning representa un paradigma de aprendizaje por refuerzo que opera bajo el principio de maximizar la recompensa acumulada futura. Su implementación se considera particularmente adecuada para este problema debido a la naturaleza secuencial de las decisiones del ratón, donde cada acción impacta directamente en el estado futuro del sistema. 

Ventajas Esperadas para el Dominio del Juego 

     Capacidad de aprender políticas óptimas en entornos deterministas
     Manejo eficiente de espacios de estado discretos
     Convergencia garantizada en entornos finitos
     

Consideraciones de Implementación 

Se anticipa que Q-Learning requerirá: 

     Discretización del espacio de estado para manejar la complejidad
     Optimización de la función Q mediante técnicas de exploración-explotación
     Manejo de la dimensionalidad del estado (posiciones, energía, olor)
     

SARSA - Enfoque Basado en Experiencia Real
Fundamentación Teórica 

SARSA se postula como algoritmo complementario debido a su capacidad de aprender políticas en entornos estocásticos. Como método que actualiza los valores basándose en la experiencia real del agente, ofrece ventajas significativas para capturar la dinámica del juego en tiempo real. 

Ventajas Esperadas para el Dominio del Juego 

     Adaptabilidad a cambios en el entorno
     Manejo de incertidumbre en la percepción sensorial
     Estabilidad en entornos no deterministas
     

Consideraciones de Implementación 

Se proyecta que SARSA necesitará: 

     Gestión de la exploración en entornos con percepción parcial
     Actualización incremental de los valores de estado-acción
     Balance entre recompensas inmediatas y futuras
     

Complementariedad de los Enfoques 

La selección de estos dos algoritmos proporciona visiones complementarias del problema: 

     Q-Learning ofrece una perspectiva "óptima" basada en valores teóricos
     SARSA proporciona una perspectiva "realista" basada en experiencia práctica
     

Esta combinación algorítmica se considera óptima para el problema debido a: 

     Naturaleza del entorno: Laberinto con percepción sensorial parcial
     Dinámica del juego: Decisiones secuenciales con impacto futuro
     Objetivos del proyecto: Desarrollar un agente capaz de aprender estrategias de escape eficientes
     
