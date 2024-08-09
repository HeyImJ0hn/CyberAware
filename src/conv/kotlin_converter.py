import os

class KotlinConverter:
    
    @staticmethod
    def convert_to_kotlin(game):
        game_name = game.game_name
        entities = game.get_entities()
        entities = []
        
        
        # App Screens
        app_nav_file = '''package dev.jpires.cyberawarebaseapp.navigation

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
        '''
        for entity in entities:
            string = f'"{entity.id}" -> BaseScreen(\n\
                screenId=screenId, "{entity.text}", true, R.drawable.pexels, buttons = listOf('
            
            for option in entity.options:
                string += f'{{modifier -> OptionButton(modifier, "{option.text}") {{ navController.navigate("base/{str(option.entity.id)}") }} }},'
                
            string += f'))'
        app_nav_file +='''
            }
        }
    }
}
        '''
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'android', 'app', 'src', 'main', 'java', 'dev', 'jpires', 'cyberawarebaseapp', 'navigation', 'AppNavigation.kt')
        with open(file_path, 'w') as file:
            file.write(app_nav_file)
            
            
            
            
        # Change app name in strings.xml
        strings_file = f'''<resources>
    <string name="app_name">{game_name}</string>
    <string name="title_activity_home_screen">HomeScreen</string>
    <string name="title_activity_app_navigation">AppNavigation</string>
</resources>
        '''
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'android', 'app', 'src', 'main', 'res', 'values', 'strings.xml')
        with open(file_path, 'w') as file:
            file.write(strings_file)
            
            
            
            
        # Change app name in settings.gradle.kts
        settings_file = f'''pluginManagement {{
    repositories {{
        google {{
            content {{
                includeGroupByRegex("com\\\\.android.*")
                includeGroupByRegex("com\\\\.google.*")
                includeGroupByRegex("androidx.*")
            }}
        }}
        mavenCentral()
        gradlePluginPortal()
    }}
}}
dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
    }}
}}

rootProject.name = "{game_name}"
include(":app")
        '''
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'android', 'settings.gradle.kts')
        with open(file_path, 'w') as file:
            file.write(settings_file)
        
        
        
        # Change app name in build.gradle.kts
        # TODO: Change app version code and version name
        build_file = f'''plugins {{
    alias(libs.plugins.android.application)
    alias(libs.plugins.jetbrains.kotlin.android)
}}

android {{
    namespace = "dev.jpires.{game_name.lower().replace(" ", "").replace("_", "").replace("-", "")}"
    compileSdk = 34

    defaultConfig {{
        applicationId = "dev.jpires.{game_name.lower().replace(" ", "").replace("_", "").replace("-", "")}"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {{
            useSupportLibrary = true
        }}
    }}

    buildTypes {{
        release {{
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }}
    }}
    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }}
    kotlinOptions {{
        jvmTarget = "1.8"
    }}
    buildFeatures {{
        compose = true
    }}
    composeOptions {{
        kotlinCompilerExtensionVersion = "1.5.1"
    }}
    packaging {{
        resources {{
            excludes += "/META-INF/{{AL2.0,LGPL2.1}}"
        }}
    }}
}}

dependencies {{

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)

    implementation("androidx.compose.ui:ui:1.6.7")
    implementation("androidx.navigation:navigation-compose:2.7.7")

    implementation("com.google.android.exoplayer:exoplayer:2.19.1")
    implementation("androidx.media3:media3-exoplayer:1.3.1")
    implementation("androidx.media3:media3-ui:1.3.1")
}}'''    

        file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'android', 'app', 'build.gradle.kts')
        with open(file_path, 'w') as file:
            file.write(build_file)