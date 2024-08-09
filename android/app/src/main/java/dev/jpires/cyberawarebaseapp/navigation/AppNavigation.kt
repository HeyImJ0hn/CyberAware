package dev.jpires.cyberawarebaseapp.navigation

import androidx.activity.compose.BackHandler
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import dev.jpires.cyberawarebaseapp.R
import dev.jpires.cyberawarebaseapp.screens.BaseScreen
import dev.jpires.cyberawarebaseapp.screens.HomeScreen
import dev.jpires.cyberawarebaseapp.screens.OptionButton

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
        
            }
        }
    }
}
        