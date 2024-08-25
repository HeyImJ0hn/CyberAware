package dev.cyberaware.burlaporemail.navigation

import androidx.activity.compose.BackHandler
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import dev.cyberaware.burlaporemail.R
import dev.cyberaware.burlaporemail.screens.BaseScreen
import dev.cyberaware.burlaporemail.screens.HomeScreen
import dev.cyberaware.burlaporemail.screens.OptionButton

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onNavigateToBaseScreen = { screenId ->
                    navController.navigate("base/$screenId")
                }
            )
        }

        composable(
            "base/{screenId}",
            arguments = listOf(navArgument("screenId") { type = NavType.StringType })
        ) { backStackEntry ->
            BackHandler(true) {
                // Do nothing
            }

            val screenId = backStackEntry.arguments?.getString("screenId") ?: return@composable
            when (screenId) {
        				"0" -> BaseScreen(
                	screenId=screenId, """""", true, R.drawable.pexels, buttons = listOf(
					{modifier -> OptionButton(modifier, "Começar") { navController.navigate("base/1") } },
				))
				"1" -> BaseScreen(
                	screenId=screenId, """Neste jogo, serás desafiado a usar o teu conhecimento e intuição para identificar possíveis
burlas digitais. A internet pode ser um lugar perigoso, repleto de esquemas que procuram enganar
os mais desatentos. Desde emails suspeitos a links fraudulentos, precisas de estar atento a todos 
os detalhes. Vais enfrentar uma série de exercícios que simulam situações reais.

Lembra-te, a tua segurança online depende da tua capacidade de identificar o que é verdadeiro e
o que é uma burla. Vamos começar!""", true, R.drawable.pexels, buttons = listOf(
					{modifier -> OptionButton(modifier, "Responder ao email") { navController.navigate("base/2") } },
					{modifier -> OptionButton(modifier, "Ignorar Email") { navController.navigate("base/3") } },
					{modifier -> OptionButton(modifier, "Teste 1") { navController.navigate("base/8") } },
					{modifier -> OptionButton(modifier, "Teste 2") { navController.navigate("base/9") } },
				))
				"2" -> BaseScreen(
                	screenId=screenId, """""", true, R.drawable.pexels, buttons = listOf(
					{modifier -> OptionButton(modifier, "Sim") { navController.navigate("base/4") } },
					{modifier -> OptionButton(modifier, "Não") { navController.navigate("base/6") } },
				))
				"3" -> BaseScreen(
                	screenId=screenId, """""", true, R.drawable.pexels, buttons = listOf(
					{modifier -> OptionButton(modifier, "Finalizar") { navController.navigate("base/7") } },
				))
				"4" -> BaseScreen(
                	screenId=screenId, """""", true, R.drawable.pexels, buttons = listOf(
				))
				"6" -> BaseScreen(
                	screenId=screenId, """""", true, R.drawable.pexels, buttons = listOf(
				))
				"7" -> BaseScreen(
                	screenId=screenId, """""", true, R.drawable.pexels, buttons = listOf(
				))
				"8" -> BaseScreen(
                	screenId=screenId, """""", true, R.drawable.pexels, buttons = listOf(
				))
				"9" -> BaseScreen(
                	screenId=screenId, """""", true, R.drawable.pexels, buttons = listOf(
				))

            }
        }
    }
}
        